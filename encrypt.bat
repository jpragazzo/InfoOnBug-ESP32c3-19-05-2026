espsecure encrypt_flash_data --aes_xts --keyfile key.bin --address 0xD000 --output ..\build\enc\partition-table-enc.bin ..\build\partition_table\partition-table.bin

espsecure encrypt_flash_data --aes_xts --keyfile key.bin --address 0x20000 --output ..\build\enc\txbt-enc.bin ..\build\txbt.bin

espsecure encrypt_flash_data --aes_xts --keyfile key.bin --address 0x0 --output ..\build\enc\bootloader-enc.bin ..\build\bootloader\bootloader.bin