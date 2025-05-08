import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
import time
import random
from PIL import Image

# Konfigurasi halaman
st.set_page_config(
    page_title="ABM Lalu Lintas Tuasan Medan",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS untuk memperindah tampilan
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .sidebar .sidebar-content {
        background-color: #2c3e50;
        color: white;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        padding: 10px 24px;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
    .stSlider>div>div>div>div {
        background-color: #3498db;
    }
    .metric {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Header aplikasi
st.title("🚗 PEMODELAN ARUS KENDARAAN MENGGUNAKAN AGENT-BASED MODELING")
st.subheader("Studi Kasus: Lalu Lintas Jalan Tuasan, Medan")

# Sidebar untuk parameter simulasi
with st.sidebar:
    st.header("⚙️ Parameter Simulasi")
    
    # Upload gambar peta
    uploaded_file = st.file_uploader("Upload peta jalan (opsional)", type=["png", "jpg", "jpeg"])
    
    # Parameter dasar
    num_agents = st.slider("Jumlah Kendaraan", 10, 200, 50, 10)
    sim_speed = st.slider("Kecepatan Simulasi", 1, 10, 5)
    max_speed = st.slider("Kecepatan Maksimal Kendaraan (km/jam)", 20, 120, 60, 5)
    road_width = st.slider("Lebar Jalan (pixel)", 3, 15, 5, 1)
    sim_duration = st.slider("Durasi Simulasi (detik)", 30, 300, 120, 30)
    
    # Parameter lanjutan
    with st.expander("Parameter Lanjutan"):
        prob_slowdown = st.slider("Probabilitas Perlambatan", 0.0, 0.5, 0.1, 0.01)
        prob_lane_change = st.slider("Probabilitas Ganti Lajur", 0.0, 0.3, 0.05, 0.01)
        min_distance = st.slider("Jarak Aman Minimum (pixel)", 1, 10, 3, 1)
        traffic_light = st.checkbox("Sinyal Lalu Lintas", True)
        if traffic_light:
            light_cycle = st.slider("Siklus Lampu Lalu Lintas (detik)", 10, 120, 60, 5)
    
    # Tombol simulasi
    run_simulation = st.button("Mulai Simulasi")
    st.markdown("---")
    st.markdown("**Teknologi:**")
    st.markdown("- Python 3.9")
    st.markdown("- Streamlit")
    st.markdown("- Matplotlib")
    st.markdown("- NumPy")
    st.markdown("---")
    st.markdown("**Kelompok:**")
    st.markdown("- Nama Anggota 1")
    st.markdown("- Nama Anggota 2")
    st.markdown("- Nama Anggota 3")

# Deskripsi aplikasi
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("""
    Aplikasi ini mensimulasikan arus lalu lintas di Jalan Tuasan, Medan menggunakan pendekatan **Agent-Based Modeling (ABM)**. 
    Setiap kendaraan dimodelkan sebagai agen yang memiliki perilaku independen berdasarkan aturan tertentu.
    """)
    
    # Tampilkan gambar peta jika diupload
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Peta Jalan Tuasan Medan", use_column_width=True)
    else:
        # Gambar default (peta sederhana)
        st.image("https://via.placeholder.com/800x400?text=Peta+Jalan+Tuasan+Medan", 
                caption="Peta Jalan Tuasan Medan (Contoh)", use_column_width=True)

with col2:
    st.markdown("### 📊 Metrik Utama")
    st.markdown("""
    <div class="metric">
        <h4>Kepadatan Lalu Lintas</h4>
        <p style="font-size: 24px; font-weight: bold; color: #3498db;">-</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="metric">
        <h4>Rata-rata Kecepatan</h4>
        <p style="font-size: 24px; font-weight: bold; color: #3498db;">- km/jam</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="metric">
        <h4>Waktu Tempuh</h4>
        <p style="font-size: 24px; font-weight: bold; color: #3498db;">- menit</p>
    </div>
    """, unsafe_allow_html=True)

# Kelas untuk model lalu lintas
class TrafficModel:
    def __init__(self, width=100, height=100, num_agents=50, road_width=5, max_speed=5):
        self.width = width
        self.height = height
        self.num_agents = num_agents
        self.road_width = road_width
        self.max_speed = max_speed
        self.agents = []
        self.traffic_lights = []
        self.initialize_agents()
        self.initialize_traffic_lights()
        
    def initialize_agents(self):
        # Inisialisasi kendaraan secara acak di jalan
        for _ in range(self.num_agents):
            lane = random.randint(0, 1)  # 0 untuk atas, 1 untuk bawah
            if lane == 0:
                x = random.randint(0, self.width)
                y = self.height // 2 - self.road_width // 2 + random.randint(0, self.road_width)
                direction = 1  # ke kanan
            else:
                x = random.randint(0, self.width)
                y = self.height // 2 + self.road_width // 2 + random.randint(0, self.road_width)
                direction = -1  # ke kiri
                
            speed = random.randint(1, self.max_speed)
            self.agents.append({
                'x': x,
                'y': y,
                'speed': speed,
                'direction': direction,
                'desired_speed': speed,
                'lane': lane
            })
    
    def initialize_traffic_lights(self):
        # Tambahkan traffic light di tengah jalan
        self.traffic_lights.append({
            'x': self.width // 2,
            'y': self.height // 2 - self.road_width - 2,
            'state': 'red',  # 'red', 'yellow', 'green'
            'timer': 0,
            'cycle': 60  # detik
        })
        
        self.traffic_lights.append({
            'x': self.width // 2,
            'y': self.height // 2 + self.road_width + 2,
            'state': 'green',
            'timer': 0,
            'cycle': 60
        })
    
    def update(self):
        # Update traffic lights
        for light in self.traffic_lights:
            light['timer'] += 1
            if light['timer'] >= light['cycle']:
                light['timer'] = 0
                if light['state'] == 'green':
                    light['state'] = 'yellow'
                elif light['state'] == 'yellow':
                    light['state'] = 'red'
                else:
                    light['state'] = 'green'
        
        # Update agents
        for agent in self.agents:
            # Aturan dasar: percepat jika di bawah kecepatan yang diinginkan
            if agent['speed'] < agent['desired_speed']:
                agent['speed'] = min(agent['speed'] + 1, agent['desired_speed'])
            
            # Periksa kendaraan di depan
            min_dist = float('inf')
            for other in self.agents:
                if agent != other and agent['lane'] == other['lane']:
                    if (agent['direction'] > 0 and other['x'] > agent['x']) or (agent['direction'] < 0 and other['x'] < agent['x']):
                        dist = abs(other['x'] - agent['x'])
                        if dist < min_dist:
                            min_dist = dist
                            if dist < 5:  # jarak aman
                                agent['speed'] = min(agent['speed'], other['speed'])
            
            # Periksa traffic light
            for light in self.traffic_lights:
                if abs(agent['x'] - light['x']) < 10 and abs(agent['y'] - light['y']) < 5:
                    if light['state'] in ['red', 'yellow']:
                        agent['speed'] = 0
            
            # Probabilitas perlambatan acak
            if random.random() < prob_slowdown:
                agent['speed'] = max(0, agent['speed'] - 1)
            
            # Probabilitas ganti lajur
            if random.random() < prob_lane_change and min_dist < 10:
                agent['lane'] = 1 - agent['lane']
                agent['y'] = self.height // 2 - self.road_width // 2 + random.randint(0, self.road_width) if agent['lane'] == 0 else self.height // 2 + self.road_width // 2 + random.randint(0, self.road_width)
            
            # Update posisi
            agent['x'] = (agent['x'] + agent['speed'] * agent['direction']) % self.width

# Fungsi untuk menjalankan simulasi
def run_simulation():
    st.info("🚦 Memulai simulasi lalu lintas...")
    
    # Inisialisasi model
    model = TrafficModel(
        width=200,
        height=100,
        num_agents=num_agents,
        road_width=road_width,
        max_speed=max_speed // 10  # konversi dari km/jam ke pixel/langkah
    )
    
    # Setup plot
    fig, ax = plt.subplots(figsize=(12, 6))
    plt.axis('off')
    plt.title(f"Simulasi Lalu Lintas Jalan Tuasan Medan\nJumlah Kendaraan: {num_agents}, Kecepatan Maks: {max_speed} km/jam")
    
    # Warna untuk visualisasi
    cmap = ListedColormap(['white', 'gray', 'red', 'yellow', 'green'])
    
    # Fungsi update untuk animasi
    def update(frame):
        ax.clear()
        ax.axis('off')
        
        # Gambar jalan
        road_top = model.height // 2 - model.road_width
        road_bottom = model.height // 2 + model.road_width
        ax.add_patch(plt.Rectangle((0, road_top), model.width, model.road_width * 2, color='gray', alpha=0.3))
        
        # Garis tengah jalan
        ax.plot([0, model.width], [model.height // 2, model.height // 2], 'w--', linewidth=1, alpha=0.5)
        
        # Gambar traffic light
        for light in model.traffic_lights:
            color = 'red' if light['state'] == 'red' else 'yellow' if light['state'] == 'yellow' else 'green'
            ax.add_patch(plt.Circle((light['x'], light['y']), 2, color=color))
        
        # Gambar kendaraan
        for agent in model.agents:
            color = 'blue' if agent['direction'] > 0 else 'orange'
            ax.add_patch(plt.Circle((agent['x'], agent['y']), 1, color=color))
            # Panah untuk menunjukkan arah
            dx = 2 * agent['direction']
            ax.arrow(agent['x'], agent['y'], dx, 0, head_width=1, head_length=1, fc=color, ec=color)
        
        model.update()
        
        # Hitung metrik
        avg_speed = sum(a['speed'] for a in model.agents) / len(model.agents) * 10  # konversi ke km/jam
        density = len(model.agents) / (model.width * model.road_width * 2)
        
        # Update metrik di sidebar
        with col2:
            st.markdown(f"""
            <div class="metric">
                <h4>Kepadatan Lalu Lintas</h4>
                <p style="font-size: 24px; font-weight: bold; color: #3498db;">{density:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric">
                <h4>Rata-rata Kecepatan</h4>
                <p style="font-size: 24px; font-weight: bold; color: #3498db;">{avg_speed:.1f} km/jam</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric">
                <h4>Waktu Tempuh</h4>
                <p style="font-size: 24px; font-weight: bold; color: #3498db;">{(model.width / (avg_speed/10 + 0.1)) / 60:.1f} menit</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Jalankan animasi
    with st.spinner("Menjalankan simulasi..."):
        ani = animation.FuncAnimation(fig, update, frames=sim_duration, interval=1000//sim_speed)
        
        # Tampilkan animasi di Streamlit
        st.pyplot(fig)
        
        # Simpan animasi sebagai GIF
        with st.expander("Simpan Hasil Simulasi"):
            gif_path = "traffic_simulation.gif"
            ani.save(gif_path, writer='pillow', fps=sim_speed)
            st.success(f"Simulasi berhasil disimpan sebagai GIF!")
            st.download_button(
                label="Unduh GIF Simulasi",
                data=open(gif_path, "rb").read(),
                file_name="traffic_simulation_tuasan_medan.gif",
                mime="image/gif"
            )
    
    st.success("✅ Simulasi selesai!")

# Jalankan simulasi jika tombol ditekan
if run_simulation:
    run_simulation()
else:
    st.warning("⚠️ Silakan atur parameter simulasi di sidebar dan klik 'Mulai Simulasi'")

# Bagian analisis hasil
st.markdown("---")
st.header("📊 Analisis Hasil Simulasi")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Grafik Arus vs Kepadatan")
    # Contoh data dummy
    density = np.linspace(0, 1, 20)
    flow = 80 * density * (1 - density)  # Hubungan fundamental
    fig, ax = plt.subplots()
    ax.plot(density, flow, 'b-')
    ax.set_xlabel("Kepadatan (kendaraan/pixel)")
    ax.set_ylabel("Arus (kendaraan/jam)")
    ax.set_title("Hubungan Arus vs Kepadatan")
    st.pyplot(fig)

with col2:
    st.markdown("### Distribusi Kecepatan")
    # Contoh data dummy
    speeds = np.random.normal(40, 10, 1000)
    fig, ax = plt.subplots()
    ax.hist(speeds, bins=20, color='orange', alpha=0.7)
    ax.set_xlabel("Kecepatan (km/jam)")
    ax.set_ylabel("Frekuensi")
    ax.set_title("Distribusi Kecepatan Kendaraan")
    st.pyplot(fig)

# Penutup
st.markdown("---")
st.markdown("""
### 🎯 Kesimpulan
Simulasi Agent-Based Modeling ini memberikan wawasan tentang dinamika lalu lintas di Jalan Tuasan Medan. 
Dengan memvariasikan parameter, kita dapat memprediksi bagaimana perubahan kondisi jalan atau volume kendaraan 
akan mempengaruhi arus lalu lintas.
""")

st.markdown("""
### 📚 Referensi
1. Nagel, K., & Schreckenberg, M. (1992). A cellular automaton model for freeway traffic.
2. Helbing, D. (2001). Traffic and related self-driven many-particle systems.
3. Medan City Traffic Report (2023).
""")
