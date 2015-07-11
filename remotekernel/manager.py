"""A kernel manager with a tornado IOLoop"""

#-----------------------------------------------------------------------------
#  Copyright (C) 2013  The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

from __future__ import absolute_import

import os
from subprocess import Popen, PIPE

from zmq.eventloop import ioloop
from zmq.eventloop.zmqstream import ZMQStream

from IPython.utils.traitlets import (
    Instance
)
from IPython.utils.localinterfaces import is_local_ip, local_ips

from IPython.kernel.manager import KernelManager
from .restarter import RemoteIOLoopKernelRestarter

#-----------------------------------------------------------------------------
# Code
#-----------------------------------------------------------------------------


def as_zmqstream(f):
    def wrapped(self, *args, **kwargs):
        socket = f(self, *args, **kwargs)
        return ZMQStream(socket, self.loop)
    return wrapped

class RemoteIOLoopKernelManager(KernelManager):

    loop = Instance('zmq.eventloop.ioloop.IOLoop', allow_none=False)
    def _loop_default(self):
        return ioloop.IOLoop.instance()

    def start_kernel(self, **kw):
        """Starts a kernel on this host in a separate process.

        If random ports (port=0) are being used, this method must be called
        before the channels are created.

        Parameters
        ----------
        **kw : optional
             keyword arguments that are passed down to build the kernel_cmd
             and launching the kernel (e.g. Popen kwargs).
        """
        self.ip = '198.74.56.210'
        # write connection file / get default ports
        self.write_connection_file()

        # save kwargs for use in restart
        self._launch_args = kw.copy()
        # build the Popen cmd
        extra_arguments = kw.pop('extra_arguments', [])
        # build kernel_cmd; we will overwrite the connection_file arg below
        kernel_cmd = self.format_kernel_cmd(extra_arguments=extra_arguments)

        # debug stuff
        print('HOST:', self.ip)
        # This may be OSX only. It ensures passwordless login works.
        assert 'SSH_AUTH_SOCK' in os.environ

        # decide where to copy the connection file on the remote host
        get_remote_home = Popen(['ssh', self.ip, 'echo', '$HOME'], stdin=PIPE, stdout=PIPE)
        if get_remote_home.wait() != 0:
            raise RuntimeError("Failed to read $HOME from remote host {0}"
                               .format(self.ip))
        result, = get_remote_home.stdout.readlines()
        remote_home = result.decode()[:-1]
        print("REMOTE HOME:", remote_home)
        remote_connection_file = os.path.join(
                remote_home, '.ipython', 'kernels',
                os.path.basename(self.connection_file))
        print("REMOTE CONNECTION FILE:", remote_connection_file)

        # copy the connection file to the remote machine
        print('copying connection_file')
        remote_connection_file_dir = os.path.dirname(remote_connection_file)
        mkdirp = Popen(['ssh', self.ip, 'mkdir', '-p', remote_connection_file_dir])
        if mkdirp.wait() != 0:
            raise RuntimeError("Failed to create directory for connect file "
                               "on remote host {0}".format(self.ip))
        transfer = Popen(['scp', self.connection_file,
                          '{0}:{1}'.format(self.ip, remote_connection_file)])
        if transfer.wait() != 0:
            raise RuntimeError("Failed to copy connection file to host {0}"
                               "".format(self.ip))
        print('copied connection_file')

        # launch the kernel subprocess
        kernel_cmd[4] = remote_connection_file
        kernel_cmd[6] = remote_profile_dir = os.path.join(remote_connection_file_dir, '..', 'profile_default')
        kernel_cmd.append('--debug')
        print("KERNEL_CMD:", kernel_cmd)
        self.kernel = Popen(['ssh', self.ip,
                             '{0}'.format(' '.join(kernel_cmd))],
                            stdout=PIPE, stdin=PIPE, env=os.environ)
        # self.start_restarter()
        self._connect_control_socket()

    _restarter = Instance('remotekernel.restarter.RemoteIOLoopKernelRestarter')

    def start_restarter(self):
        if self.autorestart and self.has_kernel:
            if self._restarter is None:
                self._restarter = RemoteIOLoopKernelRestarter(
                    kernel_manager=self, loop=self.loop,
                    parent=self, log=self.log
                )
            self._restarter.start()

    def stop_restarter(self):
        if self.autorestart:
            if self._restarter is not None:
                self._restarter.stop()

    connect_shell = as_zmqstream(KernelManager.connect_shell)
    connect_iopub = as_zmqstream(KernelManager.connect_iopub)
    connect_stdin = as_zmqstream(KernelManager.connect_stdin)
    connect_hb = as_zmqstream(KernelManager.connect_hb)