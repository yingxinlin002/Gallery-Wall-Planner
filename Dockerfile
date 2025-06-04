FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

# --- Authentik ENV variables (defaults, can be overridden at runtime) ---
ENV AUTHENTIK_CLIENT_ID="default-client-id"
ENV AUTHENTIK_CLIENT_SECRET="default-client-secret"
ENV AUTHENTIK_METADATA_URL="https://auth.example.com/application/o/application-slug/.well-known/openid-configuration"
ENV AUTHENTIK_SCOPE="openid email profile"
ENV AUTHENTIK_REDIRECT_URI="http://localhost:5000/auth/callback"

EXPOSE 8080
CMD ["python", "app.py"]
