remotekernel
============

With Jupyter or Jupyterhub, run kernels on remote machines.

For a different approach to the same problem, see also
https://github.com/korniichuk/rk

## Install

```
pip3 install https://github.com/danielballan/remotekernel/zipball/master
```

## Make Kernels

(See the [IPython documentation](https://ipython.org/ipython-doc/dev/development/kernels.html) for more about kernels.)

To make a kernel that will be run on a remote host, add a `host` field to the
`kernel.json`.

```
{"argv":["python", "-m", "IPython.kernel", "-f", "{connection_file}"],
 "display_name":"Python 3 on Remote",
 "host":"danallan.com"
}
```

The host can be a hostname, as in the example above, or an IP address.

It is also useful to map the first argument (`python`) to a specific Python
in, say, a conda environment. IPython (or ipykernel) and the notebook
dependencies must be installed in that environment. The environment can be
activated first so that any activation scripts are run.


```
{"argv":["source", "/opt/conda/bin/activate", "/opt/conda_envs/my_env",
         "/opt/conda_envs/my_env/bin/python",
         "-m", "IPython.kernel", "-f", "{connection_file}"],
 "display_name":"Python 3 on Remote",
 "host":"danallan.com"
}
```

## Run

First, make sure that the user who will run ipython, jupyter, or jupyterhub
can ssh into the remote machine without a password. Then:

```
jupyter notebook --MappingKernelManager.kernel_manager_class=remotekernel.manager.RemoteIOLoopKernelManager
```

## Jupyterhub Configuration

To use with Jupyterhub, add the following lines to `jupyterhub_config.py`.

```
c.Spawner.cmd = ['jupyterhub-singleuser', '--MappingKernelManager.kernel_manager_class=remotekernel.manager.RemoteIOLoopKernelManager']
c.Spawner.env_keep.append('SSH_AUTH_SOCK')
```
