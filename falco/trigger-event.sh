echo "🕵️‍♂️ Ejecutando evento sospechoso para probar Falco..."

docker run --rm alpine cat /etc/shadow > /dev/null 2>&1

echo "✅ Evento ejecutado. Revisa los logs de Falco."
