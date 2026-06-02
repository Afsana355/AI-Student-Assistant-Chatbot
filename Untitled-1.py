# ------------------------------------
# AES S-box generation + visualization
# Google Colab ready
# ------------------------------------

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors

# ------------------------------------
# GF(2^8) multiplicative inverse
# ------------------------------------
def gf_inv(a):
    if a == 0:
        return 0

    r0, r1 = 0x11b, a
    t0, t1 = 0, 1

    while r1 != 0:
        shift = (r0.bit_length() - 1) - (r1.bit_length() - 1)

        if shift < 0:
            r0, r1 = r1, r0
            t0, t1 = t1, t0
            shift = (r0.bit_length() - 1) - (r1.bit_length() - 1)

        r0 ^= (r1 << shift)
        t0 ^= (t1 << shift)

    inv = t0

    while inv.bit_length() > 8:
        shift = inv.bit_length() - 9
        inv ^= 0x11b << shift

    return inv & 0xFF

# ------------------------------------
# Build AES S-box
# ------------------------------------
def build_sbox():
    sbox = [0] * 256

    for x in range(256):
        y = gf_inv(x)

        result = 0

        for i in range(8):
            bit = (
                ((y >> i) & 1) ^
                ((y >> ((i + 4) % 8)) & 1) ^
                ((y >> ((i + 5) % 8)) & 1) ^
                ((y >> ((i + 6) % 8)) & 1) ^
                ((y >> ((i + 7) % 8)) & 1) ^
                ((0x63 >> i) & 1)
            )

            result |= (bit << i)

        sbox[x] = result

    return sbox

# Generate S-box
SBOX = build_sbox()

print("AES S-box (16x16 hex table):\n")

for i in range(16):
    row = SBOX[i*16:(i+1)*16]
    print(" ".join(f"{b:02x}" for b in row))

# ------------------------------------
# Visualize S-box
# ------------------------------------
plt.figure(figsize=(6, 6))
plt.title("AES S-box Visualization")

plt.imshow(
    [SBOX[i*16:(i+1)*16] for i in range(16)],
    interpolation="nearest",
    cmap="viridis"
)

plt.colorbar()
plt.show()

# ------------------------------------
# AES Standard S-box
# ------------------------------------
s_box = SBOX

# ------------------------------------
# PKCS#7 Padding
# ------------------------------------
def pkcs7_pad(data):
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len] * pad_len)

# ------------------------------------
# AES Helper Functions
# ------------------------------------
def sub_bytes(state):
    return np.array(
        [[s_box[b] for b in row] for row in state],
        dtype=int
    )

def shift_rows(state):
    new_state = np.zeros_like(state)

    for i in range(4):
        new_state[i] = np.roll(state[i], -i)

    return new_state

def add_round_key(state, key):
    return state ^ key

def gmul(a, b):
    p = 0

    for _ in range(8):
        if b & 1:
            p ^= a

        hi = a & 0x80
        a = (a << 1) & 0xFF

        if hi:
            a ^= 0x1b

        b >>= 1

    return p

def mix_columns(state):
    new_state = np.zeros_like(state)

    for c in range(4):
        col = state[:, c]

        new_state[0, c] = (
            gmul(col[0], 2) ^
            gmul(col[1], 3) ^
            col[2] ^
            col[3]
        )

        new_state[1, c] = (
            col[0] ^
            gmul(col[1], 2) ^
            gmul(col[2], 3) ^
            col[3]
        )

        new_state[2, c] = (
            col[0] ^
            col[1] ^
            gmul(col[2], 2) ^
            gmul(col[3], 3)
        )

        new_state[3, c] = (
            gmul(col[0], 3) ^
            col[1] ^
            col[2] ^
            gmul(col[3], 2)
        )

    return new_state

# ------------------------------------
# Visualization Function
# ------------------------------------
def visualize_state(state, title="AES State"):
    fig, ax = plt.subplots(figsize=(4, 4))

    cmap = plt.cm.viridis
    norm = mcolors.Normalize(vmin=0, vmax=255)

    ax.imshow(state, cmap=cmap, norm=norm)

    for i in range(4):
        for j in range(4):
            ax.text(
                j,
                i,
                f"{state[i, j]:02x}",
                ha='center',
                va='center',
                color='white',
                fontsize=12,
                fontweight='bold'
            )

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title)

    plt.show()

# ------------------------------------
# Prepare Plaintext
# ------------------------------------
plaintext = b'TestAESBlock123'
plaintext = pkcs7_pad(plaintext)

state = np.array(
    [[plaintext[row + 4*col] for col in range(4)] for row in range(4)],
    dtype=int
)

visualize_state(state, "Initial State")

# ------------------------------------
# Round Keys (Demo Only)
# ------------------------------------
round_keys = [
    np.random.randint(0, 256, (4, 4))
    for _ in range(11)
]

# ------------------------------------
# AES Encryption Visualization
# ------------------------------------
all_steps = []

# Initial AddRoundKey
state = add_round_key(state, round_keys[0])
all_steps.append(("Initial AddRoundKey", state.copy()))

# Main Rounds
for rnd in range(1, 10):

    state = sub_bytes(state)
    all_steps.append((f"Round {rnd}: SubBytes", state.copy()))

    state = shift_rows(state)
    all_steps.append((f"Round {rnd}: ShiftRows", state.copy()))

    state = mix_columns(state)
    all_steps.append((f"Round {rnd}: MixColumns", state.copy()))

    state = add_round_key(state, round_keys[rnd])
    all_steps.append((f"Round {rnd}: AddRoundKey", state.copy()))

# Final Round
state = sub_bytes(state)
all_steps.append(("Final Round: SubBytes", state.copy()))

state = shift_rows(state)
all_steps.append(("Final Round: ShiftRows", state.copy()))

state = add_round_key(state, round_keys[10])
all_steps.append(("Final Round: AddRoundKey - Ciphertext", state.copy()))

# ------------------------------------
# Display All Steps
# ------------------------------------
for title, st in all_steps:
    visualize_state(st, title)