"""
Generate narration audio for each scene of the encryption explainer video.
Uses SVOX Pico TTS (offline, ~natural voice) → WAV → MP3 via ffmpeg.
"""
import subprocess, os

AUDIO_DIR = "/home/user/ZeroDay/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

NARRATIONS = {
    "s1": (
        "Look at your screen right now. Every login you make, every message you send, "
        "every bank transaction you complete — all of that starts as plain, readable data. "
        "Without protection, anyone intercepting it could read it instantly. "
        "Today, we are going to cover two of the most important tools in cybersecurity — "
        "encryption and hashing. "
        "They both scramble data. But they are NOT the same thing. "
        "And confusing them? That is how security breaches happen."
    ),
    "s2": (
        "Here is the core question. If both encryption and hashing scramble data — "
        "why do we have two different things? "
        "The answer is simple: they solve completely different problems. "
        "Encryption is designed to be reversed. "
        "Hashing is designed to NEVER be reversed. "
        "That single difference changes everything about how, and when, you use each one."
    ),
    "s3": (
        "Let us start with encryption. "
        "You have a message — let us say: Hello Alice. "
        "You feed it into an encryption algorithm along with a key. "
        "Out comes ciphertext — a completely scrambled, unreadable version of your original message. "
        "Now here is the key point — literally. "
        "Because you have the key, you can run this process in reverse. "
        "Feed the ciphertext back in with the same key, "
        "and you get Hello Alice back. "
        "That reversibility is the entire point of encryption. "
        "You are locking something up so you can unlock it later. "
        "There are two main types. "
        "Symmetric encryption uses the same key to lock and unlock. "
        "AES is the gold standard here, used in everything from your Wi-Fi to your bank. "
        "Asymmetric encryption uses a pair of keys — "
        "a public key to encrypt, and a private key to decrypt. "
        "RSA is the classic example. "
        "Your browser uses this every single time it connects to a website."
    ),
    "s4": (
        "Now let us talk about hashing. "
        "Same input — Hello Alice. "
        "We run it through a hash function like SHA-256. "
        "Out comes a fixed-length string of characters called a hash, or digest. "
        "Now watch what happens when we try to go backwards. "
        "We cannot. "
        "There is no key. There is no reverse function. "
        "The hash function permanently destroys the path back to the original data. "
        "This is completely intentional. "
        "Hashing has two properties that make it incredibly useful. "
        "First: it is deterministic. "
        "Hello Alice will always produce the exact same hash. Every single time. "
        "Second — and this is the fascinating part — the avalanche effect. "
        "Change just one character. Add an exclamation mark. "
        "The output hash is completely, wildly different. "
        "Not a little different. Unrecognizably different. "
        "This is what makes hashing so powerful for detecting tampering — "
        "if even a single byte of your data changes, the hash changes completely. "
        "And you will know immediately."
    ),
    "s5": (
        "Let us lock in the differences side by side. "
        "Encryption is reversible. Hashing is not. "
        "Encryption requires a key. Hashing requires no key at all. "
        "Both produce consistent outputs for the same input. "
        "Encryption is used for secure data transmission. "
        "Hashing is used for integrity checking and storing passwords. "
        "Both are essential in modern security. "
        "But they are tools built for completely different jobs."
    ),
    "s6": (
        "Where do we actually see these in action? "
        "Every time your browser connects to a website using HTTPS, encryption is working. "
        "Your browser and the server negotiate a shared key "
        "and use AES to encrypt everything flowing between them. "
        "Your bank, your email, your messages — all encrypted in transit using TLS. "
        "Now for hashing. "
        "When you create an account on any modern website, "
        "your password is never stored as plain text. It is hashed. "
        "When you log in, the site hashes what you typed "
        "and compares it to the stored hash. "
        "They never need to see your actual password. "
        "And this is exactly why Forgot Password does not show you your old password — "
        "the site literally cannot look it up. It no longer exists in readable form. "
        "Modern systems take this even further with salting — "
        "adding a unique random value before hashing "
        "to prevent rainbow table attacks. "
        "The salt means that even two users with the same password "
        "will have completely different stored hashes."
    ),
    "s7": (
        "Here is the rule. "
        "Storing a password? Hash it. Never encrypt it. "
        "Sending a secret that someone needs to actually read later? Encrypt it. Never hash it. "
        "The classic mistake is encrypting passwords instead of hashing them. "
        "And this mistake has caused some of the biggest data breaches in history. "
        "Why? Because encryption requires a key. "
        "And if an attacker finds that key — "
        "every single password in your database is instantly readable. "
        "With hashing, even if an attacker gets the entire database, "
        "they still cannot reverse the hashes without enormous effort. "
        "Right tool. Right job. Every time."
    ),
    "s8": (
        "Let us recap. "
        "Encryption: scramble and unscramble, needs a key. "
        "Hashing: scramble permanently, no key needed. "
        "Right tool for the right job. "
        "That is what separates a developer who writes secure code "
        "from one who creates vulnerabilities. "
        "You now know the difference. "
        "Now you think like a security professional."
    ),
}

def generate(key, text):
    wav = f"{AUDIO_DIR}/{key}.wav"
    mp3 = f"{AUDIO_DIR}/{key}.mp3"
    # pico2wave TTS
    subprocess.run(["pico2wave", "-l", "en-US", "-w", wav, text], check=True)
    # Convert to MP3 with slight speed-up (0.95x → sounds slightly more natural/confident)
    subprocess.run([
        "ffmpeg", "-y", "-i", wav,
        "-filter:a", "atempo=1.05",   # 5% faster = less robotic pacing
        "-q:a", "2", mp3
    ], check=True, capture_output=True)
    os.remove(wav)

    # Get duration
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", mp3],
        capture_output=True, text=True
    )
    dur = float(result.stdout.strip())
    print(f"  {key}: {dur:.1f}s → {mp3}")
    return dur

if __name__ == "__main__":
    print("Generating narration audio...")
    durations = {}
    for key, text in NARRATIONS.items():
        durations[key] = generate(key, text)
    print("\nDurations:")
    for k, v in durations.items():
        print(f"  {k}: {v:.1f}s")
    print(f"\nTotal: {sum(durations.values()):.1f}s ({sum(durations.values())/60:.1f} min)")
