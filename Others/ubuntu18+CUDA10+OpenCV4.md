
https://gist.github.com/raulqf/f42c718a658cddc16f9df07ecc627be7

error:
```shell
CUDA backend for DNN module requires CC 5.3 or higher.  Please remove
  unsupported architectures from CUDA_ARCH_BIN option.
```

solution:
```
specifying CUDA_ARCH_BIN manually in the build/CMakeCache.txt
delete the version which is smaller than 5.3

CUDA_ARCH_BIN:STRING=5.3 6.0 6.1 7.0 7.5
```