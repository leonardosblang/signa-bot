import subprocess
import sys
import webbrowser
import time
from pathlib import Path

def main():
    web_app_path = Path(__file__).parent / "presentation" / "web" / "app.py"
    
    cmd = [
        sys.executable, 
        "-m", "streamlit", 
        "run", 
        str(web_app_path),
        "--server.port=8501",
        "--server.address=localhost",
        "--theme.base=light",
        "--theme.primaryColor=#e63946",
        "--theme.backgroundColor=#ffffff"
    ]
    
    try:
        # Start Streamlit in background
        process = subprocess.Popen(cmd)
        
        # Wait a bit and then open browser
        print("Aguardando Streamlit inicializar...")
        time.sleep(3)
        
        print("Abrindo navegador em http://localhost:8501")
        webbrowser.open("http://localhost:8501")
        
        # Wait for the process to complete
        process.wait()
        
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar Streamlit: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nStreamlit interrompido pelo utilizador")
        return 0

if __name__ == "__main__":
    sys.exit(main())