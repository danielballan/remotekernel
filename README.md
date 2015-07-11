remotekernel
============

an alternative approach to running Jupyter notebook kernels on remote machines
with jupyter or jupyterhub

See also https://github.com/korniichuk/rk

# Install

```
pip3 install remotekernel
```

# Make Kernels

To make a kernel that will be run on a remote host, add a `host` field to the `kernel.json`.

```
{"argv":["python", "-m", "IPython.kernel", "-f", "{connection_file}"],
 "display_name":"Python 3 on Remote",
  "host":"danallan.com"
}
```

It is also useful to map the first argument (`python`) to a specific Python
in, say, a conda environment. IPython and the notebook dependencies must be
installed in that environment.

# Run

First, make sure that the user running ipython, jupyter, or jupyterhub can ssh
into the remote machine without a password.

```
ipython notebook --MappingKernelManager.kernel_manager_class=remotekernel.manager.RemoteIOLoopKernelManager
```

# Jupyterhub Configuration

To use with Jupyterhub, add the following line to `jupyterhub_config.py`.

```
Spawner.cmd = ['jupyterhub-singleuser', '--MappingKernelManager.kernel_manager_class=remotekernel.manager.RemoteIOLoopKernelManager']
```
