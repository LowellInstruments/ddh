import asyncio

from bleak import BleakScanner


async def main():
    print('scanning for 10 seconds')
    devices = await BleakScanner.discover(
        return_adv=True,
        timeout=10
    )

    for d, a in devices.values():
        if 'A4:0B' in str(d):
            print(d)


if __name__ == "__main__":
    asyncio.run(main())
