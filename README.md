# HAL component for TP-Link HS100/HS110
This is a Machinekit HAL component for the TP-Link HS100/HS110
smart-plug. The HAL component uses the reverse engineered protocol
en/decryption which is described at
[SoftCheck](https://www.softscheck.com/en/reverse-engineering-tp-link-hs110/).

## Using the component
The `hal_smartplug` component can be integrated into any HAL
configuration with the following command:

Classic HAL:
``` hal
loadusr ./hal_smartplug.py -n smartplug -e -a <ip_address>
```

HAL Python:
``` python
address = "10.0.0.8"
name = "smartplug"
smartplug = hal.loadusr('./hal_smartplug.py -n %s -e -a %s' % (name, address), wait_name=name)
```

To use the component with the **HS100 (smart plug without power monitor)**
remove the optional argument `-e` from the command line.

The component has the following pins:

```
Component Pins:
  Comp   Inst Type  Dir         Value  Name                             Epsilon         Flags
    74        float OUT      0.015744  p.current                        0.000010        0
    74        bit   I/O         FALSE  p.enable                                         0
    74        float OUT         0.001  p.energy                         0.000010        0
    74        bit   OUT         FALSE  p.error                                          0
    74        float OUT             0  p.power                          0.000010        0
    74        float OUT      231.9359  p.voltage                        0.000010        0
```

## Testing
To the test HAL component with your smartplug device you modify the ip
address in the `test_hal_smartplug.py` and run `make check`. The
Smartplug should toggle a few times.
