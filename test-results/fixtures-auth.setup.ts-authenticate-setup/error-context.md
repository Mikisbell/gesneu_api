# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e5]:
    - generic [ref=e6]:
      - img [ref=e9]
      - generic [ref=e14]: Bienvenido a GesNeu
      - generic [ref=e15]: Ingrese sus credenciales para continuar
    - generic [ref=e17]:
      - generic [ref=e18]:
        - text: Email o Usuario
        - textbox "Email o Usuario" [ref=e19]:
          - /placeholder: admin@gesneu.com
      - generic [ref=e20]:
        - text: Contraseña
        - generic [ref=e21]:
          - textbox "••••••••" [ref=e22]
          - button "Mostrar contraseña" [ref=e23] [cursor=pointer]:
            - img
            - generic [ref=e24]: Mostrar contraseña
      - button "Iniciar Sesión" [ref=e25] [cursor=pointer]
    - paragraph [ref=e27]:
      - text: ¿Olvidó su contraseña?
      - link "Recuperar acceso" [ref=e28] [cursor=pointer]:
        - /url: "#"
  - button "Open Next.js Dev Tools" [ref=e34] [cursor=pointer]:
    - img [ref=e35]
```