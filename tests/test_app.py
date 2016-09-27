import os
import stat
import sys
import time
import unittest
import waeup.identifier
from waeup.identifier.app import (
    FPScanApp, detect_scanners, check_path, fpscan, scan,
    BackgroundCommand, FPScanCommand,
    )
from waeup.identifier.testing import (
    VirtualHomeProvider, VirtualHomingTestCase, create_fpscan,
    create_executable, create_python_script
    )

#
# Some infos about testing tk GUI stuff:
#
# buttons can be 'clicked' via 'invoke()'
#


class CheckPathTests(VirtualHomingTestCase):

    def test_check_path_not_existing(self):
        # the path given must exist
        self.assertRaises(ValueError, check_path, 'not-existing-path')

    def test_check_path_not_executable(self):
        # the path given must be an executable
        path = os.path.join(self.path_dir, 'some_exe')
        open(path, 'w').write('not an executable')
        self.assertRaises(ValueError, check_path, path)

    def test_check_path_with_shell_commands(self):
        # evil shell commands in path are quoted
        path = os.path.join(self.path_dir, 'exe; echo "Hi"')
        open(path, 'w').write('my executable')
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
        self.assertRaises(ValueError, check_path, path)

    def test_check_path(self):
        # valid paths are returned unchanged
        path = os.path.join(self.path_dir, 'my.exe')
        open(path, 'w').write('my script')
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
        assert check_path(path) == path

    def test_check_path_irregular_chars(self):
        # unusual chars in filenames are handled
        path = os.path.join(self.path_dir, 'my"special".exe')
        open(path, 'w').write('my script')
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
        self.assertRaises(ValueError, check_path, path)

    def test_check_path_empty_filename(self):
        # filenames must have at least one char.
        self.assertRaises(ValueError, check_path, '')

    def test_check_path_directory(self):
        # directories are not accepted.
        self.assertRaises(ValueError, check_path, self.path_dir)

    def test_check_path_none(self):
        # we cope with `None` values
        self.assertRaises(ValueError, check_path, None)


class FPScanTests(VirtualHomingTestCase):

    def write_prog(self, prog):
        path = os.path.join(self.path_dir, 'fpscan')
        open(path, 'w').write(prog)
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
        return path

    def test_fpscan_no_args(self):
        # we can call the given path
        prog = '#!%s\nprint("Hello\\nworld")\n' % sys.executable
        path = self.write_prog(prog)
        status, out, err = fpscan(path)
        assert out == 'Hello\nworld\n'
        assert status == 0
        assert err == ''

    def test_fpscan_args(self):
        # we can call 'fpscan' with args
        prog = '#!%s\nimport sys\nprint(sys.argv[1:])\n' % sys.executable
        path = self.write_prog(prog)
        status, out, err = fpscan(path, ['-v', ])
        assert out == "['-v']\n"

    def test_fpscan_err(self):
        # we can get stderr output
        prog = '#!%s\nimport sys\n' % sys.executable
        prog += 'sys.stdout.write("stdout")\nsys.stderr.write("stderr")\n'
        path = self.write_prog(prog)
        status, out, err = fpscan(path)
        assert out == 'stdout'
        assert err == 'stderr'

    def test_fpscan_returncode(self):
        # we can get the proper returncode
        prog = '#!%s\nimport sys\nsys.exit(1)' % sys.executable
        path = self.write_prog(prog)
        status, out, err = fpscan(path)
        assert status == 1


class DetectScannersTests(VirtualHomingTestCase):

    def test_detect_scanners_no_fpscan(self):
        # w/o fpscan we will not find any scanner
        self.assertRaises(ValueError, detect_scanners, 'invalid_path')

    def test_detect_scanners_no_scanners(self):
        # with no scanners avail. we will get an empty list
        path = os.path.join(self.path_dir, 'fpscan')
        open(path, 'w').write('#!%s\nprint("0")\n' % sys.executable)
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
        assert detect_scanners(path) == []

    def test_detect_scanners_single(self):
        # with scanners available we will get a single entry
        path = os.path.join(self.path_dir, 'fpscan')
        scanner_name = 'Digital Persona U.are.U 4000/4000B/4500\\n'
        scanner_values = '  2 0 1 0 1 384 290\\n'
        open(path, 'w').write('#!%s\nprint("%s%s")\n' % (
            sys.executable, scanner_name, scanner_values))
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
        assert detect_scanners(path) == [
            'Digital Persona U.are.U 4000/4000B/4500',
            ]


class ScanTests(VirtualHomingTestCase):

    def test_scan_no_fpscan(self):
        # without fpscan we cannot scan anything
        self.assertRaises(ValueError, scan, 'invalid_path', 0)

    def test_scan_invalid_dev(self):
        # we do not accept invalid dev numbers
        output = "Invalid device number: 2.\\n"
        path = create_fpscan(self.path_dir, output, ret_code=1)
        self.assertRaises(ValueError, scan, path, 2)


class AppTests(unittest.TestCase, VirtualHomeProvider):

    def setUp(self):
        self.setup_virtual_home()
        fake_fpscan = os.path.join(self.path_dir, 'fpscan')
        open(fake_fpscan, 'w').write('#!%s\nprint("0")\n' % sys.executable)
        os.chmod(fake_fpscan, os.stat(fake_fpscan).st_mode | stat.S_IEXEC)
        self.app = FPScanApp()

    def tearDown(self):
        self.teardown_virtual_home()

    def test_create(self):
        # we can create app instances
        assert self.app is not None


callback_counter = 0
callback_data = None


class BackgroundCommandTests(unittest.TestCase, VirtualHomeProvider):

    def setUp(self):
        self.setup_virtual_home()

    def tearDown(self):
        self.teardown_virtual_home()

    def test_wait_returncode(self):
        # we get the returncode
        path = os.path.join(self.path_dir, 'myscript')
        pysrc = 'sys.exit(42)'
        create_python_script(path, pysrc)
        cmd = BackgroundCommand(path)
        cmd.run()
        ret_code, stdout, stderr = cmd.wait()
        assert ret_code == 42

    def test_wait_stdout(self):
        # we can get the stdout output when wait()-ing
        path = os.path.join(self.path_dir, 'myscript')
        pysrc = 'print("Hello from myscript")'
        create_python_script(path, pysrc)
        cmd = BackgroundCommand(path)
        cmd.run()
        ret_code, stdout, stderr = cmd.wait()
        assert stdout == b'Hello from myscript\n'

    def test_wait_stderr(self):
        # we can get the stdout output when wait()-ing
        path = os.path.join(self.path_dir, 'myscript')
        pysrc = 'print("Hello from myscript")\n'
        pysrc += 'print("Hello from stderr", file=sys.stderr)'
        create_python_script(path, pysrc)
        cmd = BackgroundCommand(path)
        cmd.run()
        ret_code, stdout, stderr = cmd.wait()
        assert stdout == b'Hello from myscript\n'
        assert stderr == b'Hello from stderr\n'

    def test_startable(self):
        # we can start executables
        path = os.path.join(self.path_dir, 'myscript')
        stamp_file = os.path.join(self.path_dir, 'i_was_here')
        pysrc = 'open("%s", "w").write("I was here")' % stamp_file
        create_python_script(path, pysrc)
        cmd = BackgroundCommand(path)
        cmd.run()
        cmd.wait()
        assert os.path.isfile(stamp_file)

    def test_args(self):
        # we can pass in arguments
        path = os.path.join(self.path_dir, 'myscript')
        stamp_file = os.path.join(self.path_dir, 'i_was_here')
        pysrc = 'open("%s", "w").write(sys.argv[1])' % stamp_file
        create_python_script(path, pysrc)
        cmd = BackgroundCommand([path, 'myarg'])
        cmd.run()
        cmd.wait()
        assert open(stamp_file, 'r').read() == 'myarg'

    def test_timeout(self):
        # we can set a timeout
        path = os.path.join(self.path_dir, 'myscript')
        pysrc = 'time.sleep(10)'
        create_python_script(path, pysrc)
        cmd = BackgroundCommand(path, timeout=0.1)
        t_stamp1 = time.time()
        cmd.start()
        cmd.wait()
        t_stamp2 = time.time()
        assert t_stamp2 - t_stamp1 < 5
        assert not cmd.is_alive()
        assert cmd.returncode == -9
        assert cmd.stderr_data == b''
        assert cmd.stdout_data == b''
        # timeouts kill processes
        assert cmd.is_killed is True

    def test_callback(self):
        # a passed-in callback function is really called
        global callback_counter
        callback_counter = 0

        def mycallback(*args, **kw):
            global callback_counter
            callback_counter += 1
        path = os.path.join(self.path_dir, 'myscript')
        pysrc = 'time.sleep(0.1)'
        create_python_script(path, pysrc)
        cmd = BackgroundCommand(path, callback=mycallback)
        cmd.start()
        while cmd.is_alive():
            pass
        assert callback_counter > 0
        assert cmd.is_killed is False

    def test_callback_retcode(self):
        # we can get return codes from callbacks
        global callback_data

        callback_data = None

        def mycallback(*args, **kw):
            global callback_data
            callback_data = (args, kw)
        path = os.path.join(self.path_dir, 'myscript')
        pysrc = (
            'print("stdout output")\n'
            'print("stderr output", file=sys.stderr)\n'
            'sys.exit(42)')
        create_python_script(path, pysrc)
        cmd = BackgroundCommand(path, callback=mycallback)
        cmd.start()
        while cmd.is_alive():
            pass
        result_cmd = callback_data[0][0]
        assert result_cmd is cmd
        assert result_cmd.returncode == 42
        assert result_cmd.stdout_data == b'stdout output\n'
        assert result_cmd.stderr_data == b'stderr output\n'


class FPScanCommandTests(unittest.TestCase, VirtualHomeProvider):

    def setUp(self):
        self.setup_virtual_home()
        self.setup_fake_fpscan()

    def tearDown(self):
        self.teardown_virtual_home()

    def setup_fake_fpscan(self):
        src = os.path.join(
            os.path.dirname(waeup.identifier.__file__),
            'fake_fpscan')
        content = '#!%s\n' % (sys.executable)
        content += open(src, 'r').read()
        dst = os.path.join(self.path_dir, 'fpscan')
        create_executable(dst, content)
        self.fpscan_path = dst

    def create_fake_data_fpm(self):
        file_path = os.path.join(self.home_dir, 'data.fpm')
        open(file_path, 'wb').write(b'some fake data')
        return file_path

    def test_detect_ok(self):
        # we can detect devices
        cmd = FPScanCommand(self.fpscan_path)
        cmd.run()
        ret_code, stdout, stderr = cmd.wait()
        assert ret_code == 0
        assert stdout == (
            b'Digital Persona U.are.U 4000/4000B/4500\n'
            b'  2 0 1 0 1 384 290\n')
        assert stderr == b''

    def test_detect_fail(self):
        # we can detect missing devices
        cmd = FPScanCommand(self.fpscan_path, ['--no-device', ])
        cmd.run()
        ret_code, stdout, stderr = cmd.wait()
        assert ret_code == 0
        assert stdout == b'0\n'
        assert stderr == b''

    def test_scan_ok(self):
        # we can scan fingerprints (emulated)
        out_path = os.path.join(self.home_dir, 'data.fpm')
        cmd = FPScanCommand(self.fpscan_path, ['-s', '-o', out_path])
        cmd.run()
        ret_code, stdout, stderr = cmd.wait()
        assert cmd.is_alive() is False
        assert ret_code == 0
        assert stdout == b'ok\n'
        assert stderr == b''
        assert os.path.exists(out_path)

    def test_scan_invalid_device(self):
        # we detect missing devices when scanning
        cmd = FPScanCommand(self.fpscan_path, ['-s', '--no-device', ])
        cmd.run()
        ret_code, stdout, stderr = cmd.wait()
        assert ret_code == 1
        assert stdout == b''
        assert stderr == b'Invalid device number: 0.\n'

    def test_scan_fail(self):
        # scans can fail. We respect that
        cmd = FPScanCommand(self.fpscan_path, ['-s', '--scan-fail', ])
        cmd.run()
        ret_code, stdout, stderr = cmd.wait()
        assert cmd.is_alive() is False
        assert ret_code == 1
        assert stdout == b'fail\n'
        assert stderr == b''

    def test_compare_ok(self):
        # we can compare input with stored fingerprints
        stored_path = self.create_fake_data_fpm()
        cmd = FPScanCommand(self.fpscan_path, ['-c', '-i', stored_path])
        cmd.run()
        ret_code, stdout, stderr = cmd.wait()
        assert cmd.is_alive() is False
        assert ret_code == 0
        assert stdout == b'ok\n'
        assert stderr == b''

    def test_compare_no_match(self):
        # we can detect non-matches when comparing fingerprints
        stored_path = self.create_fake_data_fpm()
        cmd = FPScanCommand(
            self.fpscan_path, ['-c', '-i', stored_path, '--compare-no-match'])
        cmd.run()
        ret_code, stdout, stderr = cmd.wait()
        assert cmd.is_alive() is False
        assert ret_code == 0
        assert stdout == b'no-match\n'
        assert stderr == b''

    def test_compare_fail(self):
        # we can detect failing comparisons by exit status
        stored_path = self.create_fake_data_fpm()
        cmd = FPScanCommand(
            self.fpscan_path, ['-c', '-i', stored_path, '--compare-fail'])
        cmd.run()
        ret_code, stdout, stderr = cmd.wait()
        assert cmd.is_alive() is False
        assert ret_code == 1
        assert stdout == b'error: unknown reason\n'
        assert stderr == b''
