# RDT Over UDP

A simple implementation of RDT (Reliable Data Transfer) 3.0.  
You need to open 3 command lines and run in correct order: interceptor, receiver, then sender.

## Interceptor
`corruptionRate` packets will be dropped. `dropRate` of packets will be corrupted by randomly changing one byte. You can change the percentage by editing **intercepter.py**.
```bash
Usage: python interceptor.py --corruptionRate=0.01 --dropRate=0.01
```

## Receiver
```bash
python receiver.py file.txt
```

## Sender
```bash
python sender.py file.txt
```
