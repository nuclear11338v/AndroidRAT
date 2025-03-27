[app]
title = Photo Tool
package.name = phototool
package.domain = com.example
source.dir = .
source.include_exts = py
version = 1.0

requirements = python3,kivy,telethon,pyjnius

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 20
android.ndk = 19b

android.sdk_path = /home/username/android-sdk
android.ndk_path = /home/username/android-ndk-r19
