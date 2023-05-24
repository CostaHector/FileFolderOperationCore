from PySide2.QtCore import QFile, QFileInfo, QDir, QDirIterator, QIODevice
import enum
from typing import Callable

import sys
import os

DEFAULT_PATH = os.environ["USERPROFILE"] if sys.platform == "win32" else os.environ['HOME']
DEFAULT_PATH_DIR = QDir(DEFAULT_PATH)
class SystemPath:
    starredPath = DEFAULT_PATH_DIR.absoluteFilePath("Documents")


class FileOperation:
    @enum.unique
    class ErrorCode(enum.Enum):
        OK = 0
        SRC_PRE_DIR_INEXIST = 1
        SRC_FILE_INEXIST = 2
        SRC_DIR_INEXIST = 3
        SRC_INEXIST = 4
        DST_DIR_INEXIST = 5
        DST_PRE_DIR_CANNOT_MAKE = 6
        DST_FOLDER_ALREADY_EXIST = 7
        DST_FILE_ALREADY_EXIST = 8
        DST_FILE_OR_PATH_ALREADY_EXIST = 9
        CANNOT_REMOVE_FILE = 10
        CANNOT_REMOVE_DIR = 11
        CANNOT_MAKE_LINK = 12
        DST_LINK_INEXIST = 13
        CANNOT_REMOVE_LINK = 14
        UNKNOWN_ERROR = -1

    BATCH_COMMAND_LIST_TYPE = list[tuple]
    RETURN_TYPE = tuple[ErrorCode, BATCH_COMMAND_LIST_TYPE]

    @staticmethod
    def SplitDirName(fullPath: str) -> tuple[str, str]:
        ind = fullPath.rindex('/')
        if fullPath[ind - 1] == ':':
            return fullPath[:ind + 1], fullPath[(ind + 1):]
        return fullPath[:ind], fullPath[(ind + 1):]

    @staticmethod
    def rmpath(pre: str, rel: str) -> RETURN_TYPE:

        pth = QDir(pre).absoluteFilePath(rel)
        if not QDir(pth).exists():
            return FileOperation.ErrorCode.OK, list()  # already inexists
        ret = QDir(pre).rmpath(rel)
        return (FileOperation.ErrorCode.OK, ["mkpath", pre, rel]) if ret else (FileOperation.ErrorCode.CANNOT_REMOVE_DIR, list())

    @staticmethod
    def rmdir(pre: str, rel: str) -> RETURN_TYPE:

        pth = QDir(pre).absoluteFilePath(rel)
        if not QDir(pth).exists():
            return FileOperation.ErrorCode.OK, list()
        ret = QDir(pth).removeRecursively()
        return (FileOperation.ErrorCode.OK, list()) if ret else (FileOperation.ErrorCode.CANNOT_REMOVE_DIR, list())

    @staticmethod
    def rmfile(pre: str, rel: str) -> RETURN_TYPE:

        pth = QDir(pre).absoluteFilePath(rel)
        if not QFileInfo.exists(pth):
            return FileOperation.ErrorCode.OK, list()
        ret = QDir(pre).remove(rel)
        return (FileOperation.ErrorCode.OK, list()) if ret else (FileOperation.ErrorCode.CANNOT_REMOVE_FILE, list())

    @staticmethod
    def moveToTrash(pre: str, rel: str) -> RETURN_TYPE:

        pth = QDir(pre).absoluteFilePath(rel)
        if not QFile.exists(pth):
            return FileOperation.ErrorCode.OK, list()
        file = QFile(pth)
        ret = file.moveToTrash()
        return (FileOperation.ErrorCode.OK, [("rename", "", file.fileName(), "", pth)]) if ret else (
            FileOperation.ErrorCode.UNKNOWN_ERROR, list())

    @staticmethod
    def rename(pre: str, rel: str, to: str, toRel: str) -> RETURN_TYPE:
        pth = QDir(pre).absoluteFilePath(rel)
        if not QFile.exists(pth):
            return FileOperation.ErrorCode.SRC_INEXIST, list()
        absNewPath: str = QDir(to).absoluteFilePath(toRel)
        if QFile(absNewPath).exists():
            return FileOperation.ErrorCode.DST_FILE_OR_PATH_ALREADY_EXIST, list()
        cmds: FileOperation.BATCH_COMMAND_LIST_TYPE = list()
        preNewPathFolder = QFileInfo(absNewPath).absolutePath()
        if not QDir(preNewPathFolder).exists():
            preNewPathFolderRet = QDir().mkpath(preNewPathFolder)  # only remove dirs
            if not preNewPathFolderRet:
                return FileOperation.ErrorCode.DST_PRE_DIR_CANNOT_MAKE, list()
            cmds.append(("rmpath", "", preNewPathFolder))
        ret = QFile.rename(pth, absNewPath)
        if not ret:
            return FileOperation.ErrorCode.UNKNOWN_ERROR, cmds
        cmds.append(("rename", to, toRel, pre, rel))
        return FileOperation.ErrorCode.OK, cmds

    @staticmethod
    def cpfile(pre: str, rel: str, to: str) -> RETURN_TYPE:
        pth = QDir(pre).absoluteFilePath(rel)
        if not QFileInfo.exists(pth):
            return FileOperation.ErrorCode.SRC_INEXIST, list()
        if not QDir(to).exists():
            return FileOperation.ErrorCode.DST_DIR_INEXIST, list()
        
        toPth = QDir(to).absoluteFilePath(rel)
        if QFile.exists(toPth):
            return FileOperation.ErrorCode.DST_FILE_ALREADY_EXIST, list()

        cmds: FileOperation.BATCH_COMMAND_LIST_TYPE = list()
        prePath = QFileInfo(toPth).absolutePath()
        if not QDir(prePath).exists():
            prePathRet = QDir().mkpath(prePath)  # only remove dirs
            if not prePathRet:
                return FileOperation.ErrorCode.DST_PRE_DIR_CANNOT_MAKE, list()
            cmds.append(("rmpath", "", prePath))
        ret = QFile(pth).copy(toPth)
        if not ret:
            return FileOperation.ErrorCode.UNKNOWN_ERROR, cmds
        cmds.append(("rmfile", to, rel))
        return FileOperation.ErrorCode.OK, cmds

    @staticmethod
    def cpdir(pre: str, rel: str, to: str) -> RETURN_TYPE:
        pth = QDir(pre).absoluteFilePath(rel)
        if not QFile.exists(pth):
            return FileOperation.ErrorCode.SRC_INEXIST, list()
        if not QDir(to).exists():
            return FileOperation.ErrorCode.DST_DIR_INEXIST, list()
        toPth: str = QDir(to).absoluteFilePath(rel)
        if QFile.exists(toPth):
            return FileOperation.ErrorCode.DST_FOLDER_ALREADY_EXIST, list()  # dir or file
        recoverList = list()

        mkRootPthRet = QDir(to).mkpath(rel)
        if not mkRootPthRet:
            print(f"Failed QDir({to}).mkpath({rel})")
            return FileOperation.ErrorCode.UNKNOWN_ERROR, recoverList
        recoverList.append(("rmpath", to, rel))

        # or shutil.copytree(pth, toPth)
        src = QDirIterator(pth, [], QDir.NoDotAndDotDot | QDir.Dirs | QDir.Files, QDirIterator.Subdirectories)
        relN = len(pth) + 1
        while src.hasNext():
            src.next()
            fromPth = src.filePath()
            toRel = fromPth[relN:]
            toPath = QDir(toPth).absoluteFilePath(toRel)
            if src.fileInfo().isDir():  # dir
                if QFile.exists(toPath):
                    if QFileInfo(toPath).isFile():
                        return FileOperation.ErrorCode.DST_FILE_ALREADY_EXIST, recoverList
                mkpthRet = QDir(toPth).mkpath(toRel)
                if not mkpthRet:
                    print(f"Failed QDir({toPth}).mkpath({toRel})")
                    return FileOperation.ErrorCode.UNKNOWN_ERROR, recoverList
                recoverList.append(("rmpath", toPth, toRel))
            else:  # file
                cpRet = QFile(fromPth).copy(toPath)
                if not cpRet:
                    print(f"Failed QFile({fromPth}).copy({toPath})")
                    return FileOperation.ErrorCode.UNKNOWN_ERROR, recoverList
                recoverList.append(("rmfile", toPth, toRel))
        return FileOperation.ErrorCode.OK, recoverList

    @staticmethod
    def touch(pre: str, rel: str) -> RETURN_TYPE:
        if not QDir(pre).exists():
            return FileOperation.ErrorCode.DST_DIR_INEXIST, list()
        pth = QDir(pre).absoluteFilePath(rel)
        textFile = QFile(pth)
        if textFile.exists():
            return FileOperation.ErrorCode.OK, list()  # after all it exists

        cmds: FileOperation.BATCH_COMMAND_LIST_TYPE = list()
        prePath = QFileInfo(pth).absolutePath()
        if not QDir(prePath).exists():
            prePathRet = QDir().mkpath(prePath)
            if not prePathRet:
                return FileOperation.ErrorCode.DST_PRE_DIR_CANNOT_MAKE, cmds
            cmds.append(("rmpath", "", prePath))

        ret = textFile.open(QIODevice.NewOnly)
        if not ret:
            return FileOperation.ErrorCode.UNKNOWN_ERROR, cmds
        cmds.append(("rmfile", pre, rel))
        return FileOperation.ErrorCode.OK, cmds

    @staticmethod
    def mkpath(pre: str, rel: str) -> RETURN_TYPE:
        preDir = QDir(pre)
        if not preDir.exists():
            return FileOperation.ErrorCode.DST_DIR_INEXIST, list()
        if preDir.exists(rel):
            return FileOperation.ErrorCode.OK, list()  # after all it exists

        ret = preDir.mkpath(rel)
        return (FileOperation.ErrorCode.OK, [("rmpath", pre, rel)]) if ret else (
            FileOperation.ErrorCode.UNKNOWN_ERROR, list())

    @staticmethod
    def executer(aBatch: BATCH_COMMAND_LIST_TYPE, srcCommand: BATCH_COMMAND_LIST_TYPE = None) -> tuple[bool, BATCH_COMMAND_LIST_TYPE]:
        recoverList: FileOperation.BATCH_COMMAND_LIST_TYPE = list()
        failedCommandCnt = 0
        for ind, cmds in enumerate(aBatch):
            if not cmds:
                continue
            k: str = cmds[0]
            vals: tuple[str] = cmds[1:]
            ret, recover = FileOperation.LambdaTable[k](*vals)
            if ret != FileOperation.ErrorCode.OK:
                failedCommandCnt += 1
                print(f"{k}{vals}")
            if k == "moveToTrash" and srcCommand:  # name in trashbin is now changed compared with last time in trashbin
                assert len(recover) <= 1, f"moveToTrash recover command can only <= 1. Here is[{len(recover)}]"
                if len(recover) == 1:
                    srcCommand[-ind - 1] = recover[0]
                else:
                    srcCommand[-ind - 1] = tuple()
            recoverList += recover
        if failedCommandCnt != 0:
            print("Above %d command(s) failed." % failedCommandCnt)
        recoverList.reverse()  # in-place reverse
        return failedCommandCnt == 0, recoverList

    @staticmethod
    def link(pre: str, rel: str, to: str = SystemPath.starredPath) -> tuple[bool, BATCH_COMMAND_LIST_TYPE]:
        pth = QDir(pre).absoluteFilePath(rel)
        if not QFile.exists(pth):
            return FileOperation.ErrorCode.SRC_INEXIST, list()
        if not QDir(to).exists():
            return FileOperation.ErrorCode.DST_DIR_INEXIST, list()
        toPath: str = QDir(to).absoluteFilePath(rel) + ".lnk"
        toFile = QFile(toPath)

        cmds: FileOperation.BATCH_COMMAND_LIST_TYPE = list()
        if toFile.exists():
            if not QFile(toPath).moveToTrash():
                return FileOperation.ErrorCode.CANNOT_REMOVE_FILE, cmds
            cmds.append(("rename", "", toFile.fileName(), "", toPath))

        prePath = QFileInfo(toPath).absolutePath()
        if not QDir(prePath).exists():
            prePathRet = QDir().mkpath(prePath)
            if not prePathRet:
                return FileOperation.ErrorCode.DST_PRE_DIR_CANNOT_MAKE, cmds
            cmds.append(("rmpath", "", prePath))

        if not QFile.link(pth, toPath):
            return FileOperation.ErrorCode.CANNOT_MAKE_LINK, cmds
        cmds.append(("unlink", pre, rel + ".lnk", to))
        return FileOperation.ErrorCode.OK, cmds

    @staticmethod
    def unlink(pre: str, rel: str, to: str = SystemPath.starredPath) -> bool:
        cmds: FileOperation.BATCH_COMMAND_LIST_TYPE = list()
        toPath = QDir(to).absoluteFilePath(rel)
        if not QFile.exists(toPath):
            return FileOperation.ErrorCode.OK, cmds  # after all it not exist

        ret = QDir().remove(toPath)
        if not ret:
            return FileOperation.ErrorCode.CANNOT_REMOVE_LINK, cmds
        cmds.append(("link", pre, rel[:-4], to))  # move the trailing ".lnk"
        return FileOperation.ErrorCode.OK, cmds

    LambdaTable: dict[
        str, Callable[[], tuple[ErrorCode, list[tuple]]]] = \
        {"rmfile": rmfile, "rmpath": rmpath, "rmdir": rmdir, "moveToTrash": moveToTrash,
         "touch": touch, "mkpath": mkpath,
         "rename": rename,
         "cpfile": cpfile, "cpdir": cpdir,
         "link": link, "unlink": unlink}


if __name__ == "__main__":
    # ret = QFile.rename(r"D:\aaaaaaaaaaa2", r"E:\aaaaaaaaaaa2")
    fi = QDir("").absoluteFilePath("C:/")
    print(fi)
