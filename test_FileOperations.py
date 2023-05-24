from PySide2.QtCore import QDir, QFileInfo
import os
import sys
import shutil
import unittest


from FileOperation import FileOperation

DEFAULT_PATH = os.environ["USERPROFILE"] if sys.platform == "win32" else os.environ['HOME']
DEFAULT_PATH_DIR = QDir(DEFAULT_PATH)
class SystemPath:
    starredPath = DEFAULT_PATH_DIR.absoluteFilePath("Documents")


TEST_SRC_DIR = QDir(QFileInfo(__file__).absolutePath()).absoluteFilePath("FileOperationTestEnv/DONT_CHANGE")
TEST_DIR = QDir(QFileInfo(__file__).absolutePath()).absoluteFilePath("FileOperationTestEnv/COPY_REMOVABLE")


class FileOperationTest(unittest.TestCase):
    def setUp(self) -> None:
        if QDir(TEST_DIR).exists():
            QDir(TEST_DIR).removeRecursively()
        pythonCmds = shutil.copytree(TEST_SRC_DIR, TEST_DIR)
        # To specify dst is a Directory, one can use the following 2 ways:
        # way1: "echo D | xcopy \"%s\" \"%s\" /s /e /h /k"
        # way2: "xcopy \"%s\" \"%s\\\" /s /e /h /k"
        # To specify dst is a File, "echo F | xcopy \"%s\" \"%s\" /h /k", e.g.,
        # copytreeWinCmds = "echo D | xcopy \"%s\" \"%s\" /s /e /h /k" % (
        #     QDir().toNativeSeparators(TEST_SRC_DIR), QDir().toNativeSeparators(TEST_DIR))
        # ret = os.system(copytreeWinCmds)
        # if ret != 0:
        #     print("[Error] CopyTree[%s]" % copytreeWinCmds)
        return super().setUp()

    def tearDown(self):
        if QDir(TEST_DIR).exists():
            QDir(TEST_DIR).removeRecursively()
        return super().tearDown()

    def test_file_remove(self):
        self.assertTrue(QDir(TEST_DIR).exists("a.txt"), "Precondition not required.")
        ret, aBatch = FileOperation.rmfile(TEST_DIR, "a.txt")
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertFalse(QDir(TEST_DIR).exists("a.txt"))
        self.assertFalse(bool(aBatch))

    def test_folder_remove(self):
        self.assertTrue(QDir(TEST_DIR).exists("a"), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("a/a1"), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("a/a1.txt"), "Precondition not required.")
        ret, aBatch = FileOperation.rmdir(TEST_DIR, "a")
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertFalse(QDir(TEST_DIR).exists("a/a1.txt"))
        self.assertFalse(QDir(TEST_DIR).exists("a/a1"))
        self.assertFalse(QDir(TEST_DIR).exists("a"))
        self.assertFalse(bool(aBatch))

    def test_file_to_trashbin(self):
        self.assertTrue(QDir(TEST_DIR).exists("a.txt"), "Precondition not required.")

        ret, aBatch = FileOperation.moveToTrash(TEST_DIR, "a.txt")
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertFalse(QDir(TEST_DIR).exists("a.txt"), "file trashbin failed")

        self.assertTrue(bool(aBatch))
        recoverRet, _ = FileOperation.executer(aBatch[::-1])
        self.assertTrue(recoverRet, "Recover progress should succeed.")

        self.assertTrue(QDir(TEST_DIR).exists("a.txt"), "Recover not succeed")

    def test_inexist_file_to_trashbin(self):
        inexistFileName = "an inexist file blablablabla.txt"
        self.assertFalse(QDir(TEST_DIR).exists(inexistFileName), "Precondition not required.")
        ret, aBatch = FileOperation.moveToTrash(TEST_DIR, inexistFileName)
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertFalse(bool(aBatch))

    def test_folder_to_trashbin(self):
        self.assertTrue(QDir(TEST_DIR).exists("a"), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("a/a1"), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("a/a1.txt"), "Precondition not required.")

        ret, aBatch = FileOperation.moveToTrash(TEST_DIR, "a")
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertFalse(QDir(TEST_DIR).exists("a/a1.txt"), "file moveToTrash failed")
        self.assertFalse(QDir(TEST_DIR).exists("a/a1"), "folder moveToTrash failed")
        self.assertFalse(QDir(TEST_DIR).exists("a"), "folder moveToTrash failed")

        self.assertTrue(bool(aBatch))
        recoverRet, _ = FileOperation.executer(aBatch[::-1])
        self.assertTrue(recoverRet, "Recover progress should succeed.")

        self.assertTrue(QDir(TEST_DIR).exists("a"), "recover failed")
        self.assertTrue(QDir(TEST_DIR).exists("a/a1"), "recover failed")
        self.assertTrue(QDir(TEST_DIR).exists("a/a1.txt"), "recover failed")

    def test_inexist_folder_to_trashbin(self):
        inexistFolder = "an inexist folder blablablabla"
        self.assertFalse(QDir(TEST_DIR).exists(inexistFolder), "Precondition not required.")
        ret, aBatch = FileOperation.moveToTrash(TEST_DIR, inexistFolder)
        self.assertEqual(ret, FileOperation.ErrorCode.OK)  # indeed it not exists
        self.assertFalse(bool(aBatch))

    def test_file_copy(self):
        existFile = "a.txt"
        self.assertTrue(QDir(TEST_DIR).exists(existFile), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "Precondition not required.")
        self.assertFalse(QDir(TEST_DIR).exists(f"b/{existFile}"), "Precondition not required.")

        ret, aBatch = FileOperation.cpfile(TEST_DIR, existFile, f"{TEST_DIR}/b")
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertTrue(QDir(TEST_DIR).exists(f"b/{existFile}"), "cp failed")

        self.assertTrue(bool(aBatch))
        recoverRet, _ = FileOperation.executer(aBatch[::-1])
        self.assertTrue(recoverRet, "Recover progress should succeed.")

        self.assertTrue(QDir(TEST_DIR).exists(existFile), "recover failed")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "recover failed")
        self.assertFalse(QDir(TEST_DIR).exists(f"b/{existFile}"), "recover failed")

    def test_inexist_file_copy(self):
        inexistFileName = "an inexist file blablablabla.txt"
        self.assertFalse(QDir(TEST_DIR).exists(inexistFileName), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "Precondition not required.")
        self.assertFalse(QDir(TEST_DIR).exists(f"b/{inexistFileName}"), "Precondition not required.")

        ret, aBatch = FileOperation.cpfile(TEST_DIR, inexistFileName, f"{TEST_DIR}/b")
        self.assertNotEqual(ret, FileOperation.ErrorCode.OK)
        self.assertFalse(bool(aBatch))

        self.assertFalse(QDir(TEST_DIR).exists(inexistFileName), "folder struct should not change")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "folder struct should not change")
        self.assertFalse(QDir(TEST_DIR).exists(f"b/{inexistFileName}"), "folder struct should not change")

    def test_folder_copy_including_its_articles(self):
        existFile = "a"
        subDir = "a/a1"
        subFile = "a/a1.txt"
        self.assertTrue(QDir(TEST_DIR).exists(existFile), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists(subDir), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists(subFile), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "Precondition not required.")
        self.assertFalse(QDir(TEST_DIR).exists(f"b/{existFile}"), "Precondition not required.")
        self.assertFalse(QDir(TEST_DIR).exists(f"b/{subDir}"), "Precondition not required.")
        self.assertFalse(QDir(TEST_DIR).exists(f"b/{subFile}"), "Precondition not required.")

        ret, aBatch = FileOperation.cpdir(TEST_DIR, existFile, f"{TEST_DIR}/b")
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertTrue(QDir(TEST_DIR).exists(existFile), "should keep.")
        self.assertTrue(QDir(TEST_DIR).exists(subDir), "should keep.")
        self.assertTrue(QDir(TEST_DIR).exists(subFile), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "should keep.")
        self.assertTrue(QDir(TEST_DIR).exists(f"b/{subDir}"), "should copied here.")
        self.assertTrue(QDir(TEST_DIR).exists(f"b/{existFile}"), "should copied here.")
        self.assertTrue(QDir(TEST_DIR).exists(f"b/{subFile}"), "should copied here.")

        self.assertTrue(bool(aBatch))
        recoverRet, _ = FileOperation.executer(aBatch[::-1])
        self.assertTrue(recoverRet, "Recover progress should succeed.")

        self.assertTrue(QDir(TEST_DIR).exists(existFile), "should recover")
        self.assertTrue(QDir(TEST_DIR).exists(subDir), "should recover")
        self.assertTrue(QDir(TEST_DIR).exists(subFile), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "should recover")
        self.assertFalse(QDir(TEST_DIR).exists(f"b/{existFile}"), "should recover")
        self.assertFalse(QDir(TEST_DIR).exists(f"b/{subDir}"), "should recover")
        self.assertFalse(QDir(TEST_DIR).exists(f"b/{subFile}"), "should recover")

    def test_inexist_folder_copy_including_its_articles(self):
        inexistFolder = "an inexist folder blablablabla"
        self.assertFalse(QDir(TEST_DIR).exists(inexistFolder), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "Precondition not required.")
        self.assertFalse(QDir(TEST_DIR).exists(f"b/{inexistFolder}"), "Precondition not required.")

        ret, aBatch = FileOperation.cpdir(TEST_DIR, inexistFolder, f"{TEST_DIR}/b")
        self.assertNotEqual(ret, FileOperation.ErrorCode.OK)
        self.assertFalse(bool(aBatch))

        self.assertFalse(QDir(TEST_DIR).exists(inexistFolder), "should keep")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "should keep")
        self.assertFalse(QDir(TEST_DIR).exists(f"b/{inexistFolder}"), "should keep")

    def test_file_move_same_directory_unique_name(self):
        self.assertTrue(QDir(TEST_DIR).exists("a.txt"), "Precondition not required.")
        self.assertFalse(QDir(TEST_DIR).exists("a moved.txt"), "Precondition not required.")

        ret, aBatch = FileOperation.rename(TEST_DIR, "a.txt", TEST_DIR, "a moved.txt")
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertFalse(QDir(TEST_DIR).exists("a.txt"), "should be moved")
        self.assertTrue(QDir(TEST_DIR).exists("a moved.txt"), "should be move to this name")

        self.assertTrue(bool(aBatch))
        recoverRet, _ = FileOperation.executer(aBatch[::-1])
        self.assertTrue(recoverRet, "Recover progress should succeed.")

        self.assertTrue(QDir(TEST_DIR).exists("a.txt"), "should recover")
        self.assertFalse(QDir(TEST_DIR).exists("a moved.txt"), "should recover")

    def test_file_move_same_directory_conflict_name(self):
        self.assertTrue(QDir(TEST_DIR).exists("a.txt"), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("b.txt"), "Precondition not required.")

        ret, aBatch = FileOperation.rename(TEST_DIR, "a.txt", TEST_DIR, "b.txt")
        self.assertNotEqual(ret, FileOperation.ErrorCode.OK)
        self.assertFalse(bool(aBatch))

        self.assertTrue(QDir(TEST_DIR).exists("a.txt"), "should keep")
        self.assertTrue(QDir(TEST_DIR).exists("b.txt"), "should keep")

    def test_folder_move_same_directory_unique_name(self):
        self.assertTrue(QDir(TEST_DIR).exists("a"), "Precondition not required.")
        self.assertFalse(QDir(TEST_DIR).exists("a moved"), "Precondition not required.")

        ret, aBatch = FileOperation.rename(TEST_DIR, "a", TEST_DIR, "a moved")
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertFalse(QDir(TEST_DIR).exists("a"), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("a moved"), "Precondition not required.")

        self.assertTrue(bool(aBatch))
        recoverRet, _ = FileOperation.executer(aBatch[::-1])
        self.assertTrue(recoverRet, "Recover progress should succeed.")

        self.assertTrue(QDir(TEST_DIR).exists("a"), "should recover")
        self.assertFalse(QDir(TEST_DIR).exists("a moved"), "should recover")

    def test_folder_move_same_directory_conflict_name(self):
        self.assertTrue(QDir(TEST_DIR).exists("a"), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "Precondition not required.")

        ret, aBatch = FileOperation.rename(TEST_DIR, "a", TEST_DIR, "b")
        self.assertNotEqual(ret, FileOperation.ErrorCode.OK)
        self.assertFalse(bool(aBatch))

        self.assertTrue(QDir(TEST_DIR).exists("a"), "should keep")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "should keep")

    def test_file_move_jump_directory_unique_name(self):
        TO = QDir(TEST_DIR).absoluteFilePath("b")

        self.assertTrue(QDir(TEST_DIR).exists("a.txt"), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "Precondition not required.")
        self.assertFalse(QDir(TO).exists("path/to/a moved.txt"), "Precondition not required.")

        ret, aBatch = FileOperation.rename(TEST_DIR, "a.txt", TO, "path/to/a moved.txt")
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertFalse(QDir(TEST_DIR).exists("a.txt"), "should be moved")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "should keep")
        self.assertTrue(QDir(TO).exists("path/to/a moved.txt"), "should be moved to this new name")

        self.assertTrue(bool(aBatch))
        recoverRet, _ = FileOperation.executer(aBatch[::-1])
        self.assertTrue(recoverRet, "Recover progress should succeed.")

        self.assertTrue(QDir(TEST_DIR).exists("a.txt"), "should recover")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "should recover")
        self.assertFalse(QDir(TO).exists("path/to/a moved.txt"), "should recover")

    def test_file_move_jump_directory_conflict_name(self):
        TO = QDir(TEST_DIR).absoluteFilePath("b")

        self.assertTrue(QDir(TEST_DIR).exists("a.txt"), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "Precondition not required.")
        self.assertTrue(QDir(TO).exists("b1/b2.txt"), "Precondition not required.")  # conflict here

        ret, aBatch = FileOperation.rename(TEST_DIR, "a.txt", TO, "b1/b2.txt")
        self.assertNotEqual(ret, FileOperation.ErrorCode.OK)

        self.assertFalse(bool(aBatch))
        self.assertTrue(QDir(TEST_DIR).exists("a.txt"), "should keep")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "should keep")
        self.assertTrue(QDir(TO).exists("b1/b2.txt"), "should keep")

    def test_folder_move_jump_directory_unique_name(self):
        TO = QDir(TEST_DIR).absoluteFilePath("b")

        self.assertTrue(QDir(TEST_DIR).exists("a"), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("a/a1"), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("a/a1.txt"), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "Precondition not required.")
        self.assertFalse(QDir(TO).exists("path/to/a moved"), "Precondition not required.")

        ret, aBatch = FileOperation.rename(TEST_DIR, "a", TO, "path/to/a moved")
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertFalse(QDir(TEST_DIR).exists("a"), "should be moved")
        self.assertFalse(QDir(TEST_DIR).exists("a/a1"), "should be moved")
        self.assertFalse(QDir(TEST_DIR).exists("a/a1.txt"), "should be moved")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "should keep")
        self.assertTrue(QDir(TO).exists("path/to/a moved"), "should be moved to this new name")
        self.assertTrue(QDir(TO).exists("path/to/a moved/a1"), "struct under new name")
        self.assertTrue(QDir(TO).exists("path/to/a moved/a1.txt"), "struct under new name")

        self.assertTrue(bool(aBatch))
        recoverRet, _ = FileOperation.executer(aBatch[::-1])
        self.assertTrue(recoverRet, "Recover progress should succeed.")

        self.assertTrue(QDir(TEST_DIR).exists("a"), "should recover")
        self.assertTrue(QDir(TEST_DIR).exists("a/a1"), "should recover")
        self.assertTrue(QDir(TEST_DIR).exists("a/a1.txt"), "should recover")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "should recover")
        self.assertFalse(QDir(TO).exists("path/to/a moved"), "should recover")

    def test_folder_move_jump_directory_conflict_name(self):
        TO = QDir(TEST_DIR).absoluteFilePath("b")

        self.assertTrue(QDir(TEST_DIR).exists("a"), "Precondition not required.")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "Precondition not required.")
        self.assertTrue(QDir(TO).exists("b1/b2"), "Precondition not required.")  # conflict here

        ret, aBatch = FileOperation.rename(TEST_DIR, "a", TO, "b1/b2")
        self.assertNotEqual(ret, FileOperation.ErrorCode.OK)

        self.assertFalse(bool(aBatch))
        self.assertTrue(QDir(TEST_DIR).exists("a"), "should keep")
        self.assertTrue(QDir(TEST_DIR).exists("b"), "should keep")
        self.assertTrue(QDir(TO).exists("b1/b2"), "should keep")

    def test_touch_a_json_file_in_direct_path(self):
        self.assertFalse(QDir(TEST_DIR).exists("a new json file.json"), "Precondition not required.")

        ret, aBatch = FileOperation.touch(TEST_DIR, "a new json file.json")
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertTrue(QDir(TEST_DIR).exists("a new json file.json"))

        self.assertTrue(bool(aBatch))
        recoverRet, _ = FileOperation.executer(aBatch[::-1])
        self.assertTrue(recoverRet, "Recover progress should succeed.")

        self.assertFalse(QDir(TEST_DIR).exists("a new json file.json"), "should recover")

    def test_touch_a_json_file_in_relative_path(self):
        self.assertFalse(QDir(TEST_DIR).exists("path/to/a new json file.json"), "Precondition not required.")

        ret, aBatch = FileOperation.touch(TEST_DIR, "path/to/a new json file.json")
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertTrue(QDir(TEST_DIR).exists("path/to/a new json file.json"))

        self.assertTrue(bool(aBatch))
        recoverRet, _ = FileOperation.executer(aBatch[::-1])
        self.assertTrue(recoverRet, "Recover progress should succeed.")

        self.assertFalse(QDir(TEST_DIR).exists("path/to/a new json file.json"), "should recover")

    def test_touch_an_existed_txt_file_in_direct_path(self):
        self.assertTrue(QDir(TEST_DIR).exists("a.txt"), "Precondition not required.")

        ret, aBatch = FileOperation.touch(TEST_DIR, "a.txt")
        self.assertEqual(ret, FileOperation.ErrorCode.OK)

        self.assertFalse(bool(aBatch))

        self.assertTrue(QDir(TEST_DIR).exists("a.txt"), "should keep")

    def test_touch_an_existed_txt_file_in_relative_path(self):
        self.assertTrue(QDir(TEST_DIR).exists("a/a1.txt"), "Precondition not required.")

        ret, aBatch = FileOperation.touch(TEST_DIR, "a/a1.txt")
        self.assertEqual(ret, FileOperation.ErrorCode.OK)

        self.assertFalse(bool(aBatch))

        self.assertTrue(QDir(TEST_DIR).exists("a/a1.txt"), "should keep")

    def test_touch_a_folder_in_direct_path(self):
        self.assertFalse(QDir(TEST_DIR).exists("a new folder"), "Precondition not required.")

        ret, aBatch = FileOperation.touch(TEST_DIR, "a new folder")
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertTrue(QDir(TEST_DIR).exists("a new folder"))

        self.assertTrue(bool(aBatch))
        recoverRet, _ = FileOperation.executer(aBatch[::-1])
        self.assertTrue(recoverRet, "Recover progress should succeed.")

        self.assertFalse(QDir(TEST_DIR).exists("a new folder"), "should recover")

    def test_touch_a_folder_in_relative_path(self):
        self.assertFalse(QDir(TEST_DIR).exists("path/to/a new folder"), "Precondition not required.")

        ret, aBatch = FileOperation.touch(TEST_DIR, "path/to/a new folder")
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertTrue(QDir(TEST_DIR).exists("path/to/a new folder"))

        self.assertTrue(bool(aBatch))
        recoverRet, _ = FileOperation.executer(aBatch[::-1])
        self.assertTrue(recoverRet, "Recover progress should succeed.")

        self.assertFalse(QDir(TEST_DIR).exists("path/to/a new folder"), "should recover")

    def test_touch_an_existed_folder_in_direct_path(self):
        self.assertTrue(QDir(TEST_DIR).exists("a"), "Precondition not required.")

        ret, aBatch = FileOperation.touch(TEST_DIR, "a")
        self.assertEqual(ret, FileOperation.ErrorCode.OK)

        self.assertFalse(bool(aBatch))

        self.assertTrue(QDir(TEST_DIR).exists("a"), "should keep")

    def test_touch_an_existed_folder_in_relative_path(self):
        self.assertTrue(QDir(TEST_DIR).exists("a/a1"), "Precondition not required.")

        ret, aBatch = FileOperation.touch(TEST_DIR, "a/a1")
        self.assertEqual(ret, FileOperation.ErrorCode.OK)

        self.assertFalse(bool(aBatch))

        self.assertTrue(QDir(TEST_DIR).exists("a/a1"), "should keep")

    def test_link_a_file(self):
        self.assertTrue(QDir(TEST_DIR).exists("a.txt"), "Precondition not required.")
        
        ret, aBatch = FileOperation.link(TEST_DIR, "a.txt", SystemPath.starredPath)
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertTrue(QDir(TEST_DIR).exists("a.txt"))
        self.assertTrue(QDir(SystemPath.starredPath).exists("a.txt" + ".lnk"))
        self.assertTrue(bool(aBatch))
        
        recoverRet, _ = FileOperation.executer(aBatch[::-1])
        self.assertTrue(recoverRet)
        
        self.assertTrue(QDir(TEST_DIR).exists("a.txt"))
        self.assertFalse(QDir(SystemPath.starredPath).exists("a.txt" + ".lnk"))
        
        
    def test_link_a_dir(self):
        self.assertTrue(QDir(TEST_DIR).exists("a"), "Precondition not required.")
        
        ret, aBatch = FileOperation.link(TEST_DIR, "a", SystemPath.starredPath)
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertTrue(QDir(TEST_DIR).exists("a"))
        self.assertTrue(QDir(SystemPath.starredPath).exists("a" + ".lnk"))
        self.assertTrue(bool(aBatch))
        
        recoverRet, _ = FileOperation.executer(aBatch[::-1])
        self.assertTrue(recoverRet)
        
        self.assertTrue(QDir(TEST_DIR).exists("a"))
        self.assertFalse(QDir(SystemPath.starredPath).exists("a" + ".lnk"))
        
    def test_link_a_relative_file(self):
        self.assertTrue(QDir(TEST_DIR).exists("a/a1.txt"), "Precondition not required.")
        
        ret, aBatch = FileOperation.link(TEST_DIR, "a/a1.txt", SystemPath.starredPath)
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertTrue(QDir(TEST_DIR).exists("a/a1.txt"))
        self.assertTrue(QDir(SystemPath.starredPath).exists("a/a1.txt" + ".lnk"))
        self.assertTrue(bool(aBatch))
        
        recoverRet, _ = FileOperation.executer(aBatch[::-1])
        self.assertTrue(recoverRet)
        
        self.assertTrue(QDir(TEST_DIR).exists("a/a1.txt"))
        self.assertFalse(QDir(SystemPath.starredPath).exists("a/a1.txt" + ".lnk"))

    def test_link_a_relative_folder(self):
        self.assertTrue(QDir(TEST_DIR).exists("a/a1"), "Precondition not required.")
        
        ret, aBatch = FileOperation.link(TEST_DIR, "a/a1", SystemPath.starredPath)
        self.assertEqual(ret, FileOperation.ErrorCode.OK)
        self.assertTrue(QDir(TEST_DIR).exists("a/a1"))
        self.assertTrue(QDir(SystemPath.starredPath).exists("a/a1" + ".lnk"))
        self.assertTrue(bool(aBatch))
        
        recoverRet, _ = FileOperation.executer(aBatch[::-1])
        self.assertTrue(recoverRet)
        
        self.assertTrue(QDir(TEST_DIR).exists("a/a1"))
        self.assertFalse(QDir(SystemPath.starredPath).exists("a/a1" + ".lnk"))

if __name__ == "__main__":
    unittest.main()
