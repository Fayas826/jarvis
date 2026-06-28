# Chapter 15: The Vault Protocol (Ghost Mode)

This plan outlines a highly secure, zero-risk method for protecting your sensitive data during an Intruder Lockdown, without altering the dangerous Windows OS PIN.

## The Problem with Changing the Windows PIN
Changing the Windows PIN remotely via script requires deep OS registry/admin access. If the laptop powers off during the change, or the script generates a PIN and fails to send it to your phone, you are permanently locked out of your own computer. You would have to wipe the hard drive to get back in.

## The Solution: The Vault Protocol
Instead of locking you out of Windows, we will lock the *data itself*. 

When you press **"INTRUDER LOCKDOWN"** on your phone, JARVIS will execute the **Vault Protocol**:

1. **Instant Encryption:** JARVIS will take a specific folder (e.g., `c:\jarvis AI\jarvis\TopSecret`) and compress it into a highly encrypted ZIP file using a pre-set, master password that **only you know**.
2. **Ghosting:** JARVIS will instantly delete the original, unencrypted folder. 
3. **The Result:** If the intruder manages to guess your Windows PIN and logs in, they will find nothing but a locked `Vault.zip`. Your data is safe. When you get your laptop back, you simply unzip the folder using your master password.

> [!IMPORTANT]
> **User Review Required:**
> 1. Do you approve of this "Vault Protocol" method? It is 100% safe and ensures you never get locked out of your OS.
> 2. What should your **Master Vault Password** be? (I will hardcode it into the script, or we can use an environment variable).
> 3. Which folder on your laptop should act as the "Sensitive Data" folder that JARVIS will encrypt?

## Proposed Changes

### [MODIFY] `c:\jarvis AI\jarvis\backend\mobile_dominion.py`
- Import the `pyzipper` or `pyminizip` library (we will use `pyzipper` for AES encryption).
- Add a new function `execute_vault_protocol(target_folder, vault_password)`.
- Wire this function into the existing `trigger_intruder_lockdown()` method so it runs simultaneously with the Sonic Alarm and Screen Lock.

## Verification Plan
1. Create a dummy folder with test files.
2. Trigger the Intruder Lockdown from the mobile app.
3. Verify the dummy folder is deleted and replaced with a locked `Vault.zip`.
4. Manually extract `Vault.zip` using the master password to confirm data integrity.
