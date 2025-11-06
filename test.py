from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os
CAMINHO_IMAGEM = r"C:/promobotija85.png"  
print("Imagem existe?", os.path.exists(CAMINHO_IMAGEM))
print("Caminho absoluto:", os.path.abspath(CAMINHO_IMAGEM))

