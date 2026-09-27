# Keycloak configuration
## 1. Docker service
```
services:
  postgresql:
    image: postgres:16
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - '${POSTGRESQL_DATA_PATH}:/var/lib/postgresql/data'
    networks:
      - keycloak

  keycloak:
    image: quay.io/keycloak/keycloak:22.0.3
    restart: always
    command: start
    depends_on:
      - postgresql
    environment:
      KC_PROXY_ADDRESS_FORWARDING: "true"
      KC_HOSTNAME_STRICT: "false"
      KC_HOSTNAME: ${KC_HOSTNAME}
      KC_PROXY: edge
      KC_HTTP_ENABLED: "true"
      KC_DB: postgres
      KC_DB_USERNAME: ${KC_DB_USERNAME}
      KC_DB_PASSWORD: ${KC_DB_PASSWORD}
      KC_DB_URL_HOST: postgresql
      KC_DB_URL_PORT: 5432
      KC_DB_URL_DATABASE: ${POSTGRES_DB}
      KEYCLOAK_ADMIN: ${KEYCLOAK_ADMIN}
      KEYCLOAK_ADMIN_PASSWORD: ${KEYCLOAK_ADMIN_PASSWORD}
    networks:
      - caddy
      - keycloak
    labels:
      caddy: ${KC_HOSTNAME}
      caddy.reverse_proxy: "{{upstreams 8080}}"

networks:
  caddy:
    external: true
  keycloak:
```

## 2. Environment config (.env)
```
POSTGRES_USER=keycloak
POSTGRES_DB=keycloak
POSTGRES_PASSWORD=changeme
KC_HOSTNAME=login.yourdomain.com
KC_DB_USERNAME=keycloak
KC_DB_PASSWORD=changeme
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=changeme
POSTGRESQL_DATA_PATH=/opt/docker/keycloak/postgresql_data
```

## 3. Keycloak service setup
```
https://keycloak.yourdomain.com/realms/master/protocol/openid-connect/auth
https://keycloak.yourdomain.com/realms/master/protocol/openid-connect/token
https://keycloak.yourdomain.com/realms/master/protocol/openid-connect/userinfo
https://portainer.yourdomain.com/
<a href="https://keycloak.yourdomain.com/realms/master/protocol/openid-connect/logout" rel="noreferrer noopener" title="https://keycloak.yourdomain.com/realms/master/protocol/openid-connect/logout" target="_blank">https://keycloak.yourdomain.com/realms/master/protocol/openid-connect/logout</a>
```

```
email
email openid profile
```