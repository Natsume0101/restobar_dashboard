# ✅ Checklist de Despliegue y Mantenimiento

Este documento es para ti (administrador) para asegurar que todo funcione correctamente antes y después de actualizar el dashboard.

## 🛠 Antes de hacer Push (Subir cambios)

1. **Verificar Datos**:
   - ¿Ha actualizado el archivo `ventas_historicas_3anos.csv` con los datos más recientes?
   - Si cambió el nombre del archivo, actualice `analyze_restaurant_data.py` y `dashboard.py`.

2. **Probar Localmente**:
   - Ejecute `streamlit run dashboard.py` en su computadora.
   - Verifique que no haya errores rojos en pantalla.
   - Pruebe los filtros de fecha.

3. **Revisar Dependencias**:
   - Asegúrese de que `requirements.txt` tenga `streamlit==1.32.0` (crítico para iPhone).

## 🚀 Después del Auto-Despliegue (GitHub -> Streamlit Cloud)

Streamlit Cloud detectará el cambio en GitHub y actualizará la app automáticamente.

1. **Esperar**: El proceso suele tardar 1-2 minutos.
2. **Verificar Estado**: Intente abrir su link público.
   - Si ve un icono de "Cocinando/Baking" (horno) o "Upgrading", espere.
3. **Validación Rápida**:
   - Abra la app desde su celular.
   - **Prueba de Humo**: ¿Cargan los gráficos? ¿Se ven los números?
   - **Prueba de Filtro**: Cambie el rango de fechas. Si falla, es posible que el formato de fecha en el CSV haya cambiado.

## 🆘 Solución de Problemas Comunes

- **Error "ModuleNotFoundError"**: Falta una librería en `requirements.txt`.
- **Pantalla Blanca en iPhone**: Confirme que la versión de Streamlit sea 1.32.0.
- **La App no actualiza**: Vaya a su panel de Streamlit Cloud (share.streamlit.io), busque su app, haga clic en los tres puntos y seleccione **"Reboot app"**.
