"""Quick script to explore the /usage status tab"""
import os
import time
import pexpect

env = os.environ.copy()
env["TERM"] = "dumb"

child = pexpect.spawn("claude", encoding="utf-8", timeout=30, env=env)

# Wait for ready
child.expect([r"\? for shortcuts", r"[>›]", pexpect.TIMEOUT], timeout=15)
time.sleep(0.5)

# Send /usage
child.send("/usage\r")
time.sleep(0.5)
child.send("\r")
time.sleep(1.0)

# Now press Tab to go to Status
child.send("\t")
time.sleep(1.0)

# Read output
try:
    child.expect(pexpect.TIMEOUT, timeout=2)
except:
    pass

print("=== OUTPUT AFTER TAB (Status tab) ===")
print(child.before or "(no output)")
print("=== END ===")

# Exit cleanly
child.send("\x1b")
time.sleep(0.1)
child.send("/exit\r\r")
try:
    child.expect(pexpect.EOF, timeout=5)
except:
    pass
child.close()
