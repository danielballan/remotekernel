from jupyter_client.kernelspec import KernelSpec
from trailets import Unicode

class RemoteKernelSpec(KernelSpec):
    host = Unicode()

    def to_dict(self):
        res = super().to_dict()
        res['host'] = self.host
        return res
