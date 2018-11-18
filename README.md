# ESP32 AWS IoT example using Arduino SDK

[![Build Status](https://travis-ci.org/jandelgado/esp32-aws-iot.svg?branch=master)](https://travis-ci.org/jandelgado/esp32-aws-iot)

This is a fork of https://github.com/ExploreEmbedded/Hornbill-Examples
focusing on the AWS_IOT library and removing everything else. The code was
also upgraded to AWS IoT Device SDK v3.0.1. 

The library was modified so that the TLS configuration (i.e. certificates and
stuff) is _no longer_ included in the library code self, but is now passed to
the `AWS_IOT` class from the client code. This makes the library easier usable.

* original repository:  https://github.com/ExploreEmbedded/Hornbill-Examples

## pubSubTest Example

Under [examples/pubSubTest](examples/pubSubTest) the original PubSub example of
the hornbill repository is included, with the configuration externalized to a
separate file [config.h-dist](examples/pubSubTest/config.h-dist). To build the
example, copy the `config.h-dist` file to a file called `config.h` and modify
to fit your configuration:

* add WiFi configuration
* add AWS thing private key
* add AWS thing certificate 
* add AWS MQTT endpoint address

### Build

A plattformio [project](platformio.ini) and [Makefile](Makefile) is provided.

* run `make upload monitor` to build and upload the example to the ESP32 and
  start the serial monitor afterwards to see what is going on.

#### AWS IoT core notes

### MQTT endpoint

Running `aws describe-endpoint` will give you the endpoint of your MQTT and
REST service.

Alternatively, using the AWS console: The MQTT endpoint can be found under
`Test` > `Connected as ...` > `View Endpoint` or `Thing` > `(your thing)` >
`Interact` > `HTTP`. 

The secure MQTT port is 8883. To test if your MQTT endpoint is up, you could
for example issue a netcat command like `nc -v <your-iot-endpoint> 8883`.

### Attach a policy to your thing

It is important to attach a policy to your thing, otherwise no communication
will be possible.

Go to `Things` > `(your thing)` > `security` > `(your certificate)` > `policies`
and select `attach/edit policy` to add a policy similar this one:

```
{
   "Version" : "2012-10-17",
   "Statement" : [
      {
         "Action" : [
            "iot:Publish",
            "iot:Connect",
            "iot:Receive",
            "iot:Subscribe",
            "iot:GetThingShadow",
            "iot:DeleteThingShadow",
            "iot:UpdateThingShadow"
         ],
         "Effect" : "Allow",
         "Resource" : [
            "*"
         ]
      }
   ]
}
```

