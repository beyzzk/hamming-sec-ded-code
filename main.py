import tkinter as tk
from tkinter import ttk, messagebox

memory = {
    "original": None,
    "encoded": None,
    "with_error": None
}

def clear_all():
    #giriş alanlarını temizle
    entry_data.delete(0, tk.END)
    entry_error.delete(0, tk.END)
    entry_error2.delete(0, tk.END)

    #label ve text ekranını temizle
    label_status.config(text="", foreground="black")
    text_display.config(state="normal")
    text_display.delete("1.0", tk.END)
    text_display.config(state="disabled")

    #bellekteki verileri sıfırla
    memory["original"] = None
    memory["encoded"] = None
    memory["with_error"] = None

def calculate_check_bits_count(m):
    r = 0
    while (2 ** r) < (m + r + 1):
        r += 1
    return r

def is_power_of_two(n):
    return n and (n & (n - 1)) == 0

def insert_check_bit_placeholders(data_bits):
    m = len(data_bits)
    r = calculate_check_bits_count(m)
    total_len = m + r
    result = ['0'] * total_len
    j = 0  #veri bit index
    for i in range(1, total_len + 1):
        if not is_power_of_two(i):
            result[-i] = data_bits[-(j + 1)]  #sağdan sola
            j += 1
    return result

def calculate_check_bits(code_bits):
    n = len(code_bits)
    r = calculate_check_bits_count(n - calculate_check_bits_count(n))
    check = 0
    for i in range(n):
        if code_bits[i] == '1':
            position = n - i  #sağdan sola
            check ^= position
    return check  #integer form (0110=6)

def calculate_parity_bit(bits):
    #tüm bitlerin XOR'u alınır
    parity = 0
    for b in bits:
        parity ^= int(b)
    return parity

def apply_check_bits(code_bits, check_value):
    n = len(code_bits)
    for i in range(n):
        pos = n - i
        if is_power_of_two(pos):
            bit_no = (pos).bit_length() - 1
            value = (check_value >> bit_no) & 1
            code_bits[i] = str(value) 
    parity = calculate_parity_bit(code_bits)
    code_bits.insert(0, str(parity))
    return code_bits

def label_bit_positions(code_bits):
    n = len(code_bits)
    labels = [''] * n
    labels[0] = "P"  #parity bit
    d_count = 1
    for i in range(n-1, 0, -1):
        pos = n - i
        if is_power_of_two(pos):
            labels[i] = f"C{pos}"
        else:
            labels[i] = f"D{d_count}"
            d_count += 1
    return labels

def inject_error(code, position_from_right_1_based):
    n = len(code)
    index = n - position_from_right_1_based  #sağdan 1 tabanlıdan python dizisine çeviriyorum (python 0 tabanlı ve soldan indekslendigi için)
    if 0 <= index < n:
        flipped = '1' if code[index] == '0' else '0'
        return code[:index] + flipped + code[index+1:]
    return code

def detect_error(code_bits):
    return calculate_check_bits(code_bits)

def correct_error(code_bits):
    error_pos = detect_error(code_bits)
    if error_pos == 0:
        return ''.join(code_bits), -1
    n = len(code_bits)
    index = n - error_pos
    if 0 <= index < n:
        code_bits[index] = '0' if code_bits[index] == '1' else '1'
    return ''.join(code_bits), index

#GUI Fonksiyonları
def format_bits_with_labels(bits, labels, highlight_index=None, highlight_color=None):    
    spaced_labels = ""
    spaced_bits = ""
    for i, (b, lbl) in enumerate(zip(bits, labels)):
        spaced_labels += f"{lbl:<4}"
        spaced_bits += f"{b:<4}"
    return spaced_labels, spaced_bits

def update_display(highlight_error_index=None, highlight_error_color=None, highlight_correct_index=None, highlight_correct_color=None):
    #bu fonksiyon label_status yerine text widget'ı günceller
    #highlight_error_index:hata yapılan bitin indeksi
    #highlight_correct_index:düzeltme yapılan bitin indeksi

    if memory["encoded"] is None:
        text_display.config(state="normal")
        text_display.delete("1.0", tk.END)
        text_display.insert(tk.END, "Lütfen önce veri girip kodlayın.")
        text_display.config(state="disabled")
        return

    labels = label_bit_positions(memory["encoded"])
    bits = memory["with_error"] if memory["with_error"] is not None else memory["encoded"]

    spaced_labels, spaced_bits = format_bits_with_labels(bits, labels)

    text_display.config(state="normal")
    text_display.delete("1.0", tk.END)

    text_display.insert(tk.END, "Bit Pozisyonları:\n")
    text_display.insert(tk.END, spaced_labels + "\n\n")

    text_display.insert(tk.END, "Kodlu Veri:\n")
    text_display.insert(tk.END, spaced_bits + "\n\n")

    def apply_highlight(tag_name, index, color):
        char_pos = f"5.{index * 4}"
        text_display.tag_add(tag_name, char_pos, f"{char_pos}+1c")
        text_display.tag_config(tag_name, foreground=color, font=("Courier", 12, "bold"))

    if highlight_error_index is not None:
        apply_highlight("error_bit", highlight_error_index, highlight_error_color or "red")

    if highlight_correct_index is not None:
        apply_highlight("correct_bit", highlight_correct_index, highlight_correct_color or "green")

    text_display.config(state="disabled")

def write_to_memory():
    raw = entry_data.get().strip()
    if not all(c in '01' for c in raw):
        messagebox.showerror("Hata", "Lütfen sadece 0 ve 1 girin.")
        return
    if len(raw) not in (8, 16, 32):
        messagebox.showerror("Hata", "Sadece 8, 16 veya 32 bitlik veri destekleniyor.")
        return

    placeholders = insert_check_bit_placeholders(raw)
    check_value = calculate_check_bits(placeholders)
    final_bits = apply_check_bits(placeholders, check_value)

    memory["original"] = raw
    memory["encoded"] = ''.join(final_bits)
    memory["with_error"] = ''.join(final_bits)

    update_display()
    label_status.config(text=f"Veri başarıyla kodlandı.Toplam bit sayısı: {len(final_bits)}",font=("Courier", 12), foreground="green")

def apply_error():
    try:
        pos1 = int(entry_error.get().strip())
    except ValueError:
        messagebox.showerror("Hata","1.hata için geçerli bir bit pozisyonu girin.")
        return

    pos2_text = entry_error2.get().strip()
    pos2 = None
    if pos2_text:
        try:
            pos2 = int(pos2_text)
        except ValueError:
            messagebox.showerror("Hata","2.hata için geçerli bir bit pozisyonu girin.")
            return

    if memory["encoded"] is None:
        messagebox.showerror("Hata","Önce veri girin ve kodlayın.")
        return

    n = len(memory["with_error"])
    if not (1 <= pos1 <= n):
        messagebox.showerror("Hata", f"1.hata için 1 ile {n} arasında bir değer girin.")
        return
    if pos2 and not (1 <= pos2 <= n):
        messagebox.showerror("Hata", f"2.hata için 1 ile {n} arasında bir değer girin.")
        return

    faulty = inject_error(memory["encoded"], pos1)
    if pos2:
        faulty = inject_error(faulty, pos2)

    memory["with_error"] = faulty

    indices = [n - pos1]
    if pos2:
        indices.append(n - pos2)

    update_display(highlight_error_index=indices[0], highlight_error_color="red")
    if len(indices) == 2:
        update_display(highlight_error_index=indices[1], highlight_error_color="darkred")

    msg = f"{pos1}. bit ters çevrildi"
    if pos2:
        msg += f" ve {pos2}. bit ters çevrildi"
    msg += " (kırmızıyla gösterildi)."

    label_status.config(text=msg,font=("Courier", 12), foreground="darkorange")

def detect_and_correct():
    if memory["with_error"] is None:
        messagebox.showerror("Hata","Hatalı veri bulunamadı.")
        return

    bits = list(memory["with_error"])
    received_parity = int(bits[0])
    data_bits = bits[1:]

    syndrome = detect_error(data_bits)
    expected_parity = calculate_parity_bit(data_bits)

    if syndrome == 0 and received_parity == expected_parity:
        update_display()
        label_status.config(text="Hata yok.Veri doğru.\nSendrom: 0",font=("Courier", 12), foreground="blue")

    elif syndrome != 0 and received_parity != expected_parity:
        #tek hata,düzeltilebilir.
        corrected, error_index = correct_error(data_bits)
        bits = [str(expected_parity)] + list(corrected)
        memory["with_error"] = ''.join(bits)
        update_display(highlight_correct_index=error_index + 1, highlight_correct_color="green")

        pos_from_right = len(bits) - (error_index + 1)
        syndrome_str = format(syndrome, f'0{calculate_check_bits_count(len(data_bits)-calculate_check_bits_count(len(data_bits)))}b')
        label_status.config(
            text=f"Sendrom kelimesi: {syndrome_str}\n"
                f"Hatalı bit pozisyonu (sağdan): {pos_from_right}\n"
                f"Düzeltilmiş bit yeşille gösterildi.",font=("Courier", 12),
            foreground="green"
        )

    #çift hata düzeltilemez,sadece tespit edilir.
    elif syndrome != 0 and received_parity == expected_parity:
        update_display()
        label_status.config(
            text=f"Çift hata tespit edildi!\nBu durumda sendrom geçersizdir ve düzeltme yapılamaz.",font=("Courier", 12),
            foreground="red"
        )

    elif syndrome == 0 and received_parity != expected_parity:
        #sadece parity bitinde hata
        bits[0] = '0' if bits[0] == '1' else '1'
        memory["with_error"] = ''.join(bits)
        update_display(highlight_correct_index=0, highlight_correct_color="green")
        label_status.config(text="Sadece parity bitinde hata vardı, düzeltildi.",font=("Courier", 12), foreground="orange")


#Tkinter ile GUI
root = tk.Tk()
root.title("Hamming SEC-DED Code Simülatörü")
root.geometry("1000x800")
style = ttk.Style(root)
style.theme_use("clam")
style.configure(".", font=("Courier", 15)) 

#buton stilleri için
style.configure("Custom.TButton",
    background="#D32F2F",
    font=("Courier", 12, "bold"),
    padding=6,
    borderwidth=0
)
style.map("Custom.TButton",
    background=[("active", "#66BB6A")],
)

frame_main = ttk.Frame(root, padding=15)
frame_main.pack(fill="both", expand=True)

ttk.Label(frame_main, text="Veri Girişi (8, 16, 32 bit - sadece 0 ve 1):").pack(pady=5)
entry_data = ttk.Entry(frame_main, width=50)
entry_data.pack(pady=5)

btn_encode = ttk.Button(frame_main, text="Belleğe Yaz ve Kodla",style="Custom.TButton", command=write_to_memory)
btn_encode.pack(pady=7)

#hatalı bit girişi için text kutusu
ttk.Label(frame_main, text="Hangi bitte hata oluşturulsun? (en sağ:1)").pack(pady=5)
entry_error = ttk.Entry(frame_main, width=10)
entry_error.pack(pady=5) 

#ikinci hata için text kutusu
ttk.Label(frame_main, text="İkinci hata (isteğe bağlı - en sağ:1):").pack(pady=5)
entry_error2 = ttk.Entry(frame_main, width=10)
entry_error2.pack(pady=5)

btn_error = ttk.Button(frame_main, text="Hata Uygula",style="Custom.TButton", command=apply_error)
btn_error.pack(pady=7)

btn_detect_correct = ttk.Button(frame_main, text="Hatalı Veriyi Tespit Et ve Düzelt",style="Custom.TButton", command=detect_and_correct)
btn_detect_correct.pack(pady=10)

btn_clear = ttk.Button(frame_main, text="Temizle", command=clear_all)
btn_clear.pack(pady=10)

label_status = ttk.Label(frame_main, text="", foreground="black", wraplength=650, justify="left")
label_status.pack(pady=8)

text_display = tk.Text(frame_main, width=350, height=8, font=("Courier", 12), state="disabled", bg="#f0f0f0")
text_display.pack(pady=10)
ttk.Label(frame_main, text="P: Parity biti  C1, C2: Check bitleri  D1, D2: Veri bitleri", 
          foreground="#555555", anchor="w", font=("Courier", 13)).pack(fill="x", padx=5, pady=(0, 15))
root.mainloop()
