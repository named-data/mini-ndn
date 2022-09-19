
[comments]: The original author of Mini-NDN docker is Md Ashiqur Rahman (marahman@email.arizona.edu)

## Running Mini-NDN inside Docker

You can use the nightly build from GitHub package registry
```bash
docker run -m 4g --cpus=4 -it --privileged \
           -v /lib/modules:/lib/modules \
           ghcr.io/named-data/mini-ndn:master bash
```

## Building your own image

The Dockerfile can be used directly to `build` an image from scratch.

* Build with `Dockerfile`:
  * Clone the repository and type.
    ```bash
    docker build -t minindn .
    ```
  * You can then access the container through shell with,
    ```bash
    docker run -m 4g --cpus=4 -it --privileged \
           -v /lib/modules:/lib/modules \
           minindn bin/bash
    ```

### Notes:

* Memory (-m), CPU (--cpus) are recommended by Mini-NDN.
* `--privileged` is mandatory for underlying [Mininet](http://mininet.org/) to utilize virtual switch
* Root directory on `run` is `/mini-ndn` containing the installation and examples.
* GUI may not work for now due to docker and xterm setup issues and is independent from Mini-NDN.
If you intend to run the GUI, pass `-e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix` to the `docker run` command.