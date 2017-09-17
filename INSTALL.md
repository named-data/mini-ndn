Mini-NDN Installing Instructions
================================

### What equipment will I need ?

Basically, you'll need a laptop/desktop with a recent Linux distro (Ubuntu, Fedora).
We recommend Ubuntu. For this guide, the _Ubuntu 16.04 64bit LTS_ was used.
Also, note that you'll need administrative privileges in order to download and install
extra packages and also to execute **MiniNDN-WiFi**.

### Installing **MiniNDN-WiFi**

If you didn't istall any dependency of MninNDN-WiFi, Please you install according to the following setps. Otherwise, you can only select moudules that you want to install.

    step 1: $ sudo apt-get install git
    
    step 2: $ git clone https://github.com/iamxg/minindn-wifi/
 
    step 3: $ cd mininet-wifi
    
    step 4: $ sudo ./install.sh -drtmiw
install.sh options:

    -d: NFD
    
    -r: NLSR
    
    -t: NDN tools
    
    -m: mininet-wifi and dependencies
    
    -i: mini-ndn and dependencies
    
    -w: minindn-wifi
    
