import streamlit.components.v1 as components

def render_mech_3d_hud(state="IDLE", active_agent="Standby", step_info=""):
    """
    Transparent, borderless Three.js 3D mechanical gears floating directly on the page.
    state: 'IDLE' | 'WORKING' | 'READY'
    """
    palette = {
        "IDLE": {
            "gear_main": "#FF6B2C",
            "gear_sub": "#FFB088",
            "dot": "#FF6B2C",
            "pill_bg": "rgba(255, 243, 237, 0.92)",
            "pill_text": "#C8410B",
            "label": "Standby",
            "speed": 0.007,
        },
        "WORKING": {
            "gear_main": "#FF5500",
            "gear_sub": "#FF9900",
            "dot": "#FF5500",
            "pill_bg": "rgba(255, 232, 220, 0.96)",
            "pill_text": "#B83200",
            "label": f"{active_agent} ({step_info})" if step_info else active_agent,
            "speed": 0.042,
        },
        "READY": {
            "gear_main": "#10B981",
            "gear_sub": "#6EE7B7",
            "dot": "#10B981",
            "pill_bg": "rgba(236, 253, 245, 0.96)",
            "pill_text": "#065F46",
            "label": "Report Ready",
            "speed": 0.012,
        },
    }

    cfg = palette.get(state, palette["IDLE"])

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            html, body {{
                background: transparent !important;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                overflow: hidden;
                height: 225px;
                position: relative;
            }}
            #canvas-container {{
                width: 100%;
                height: 100%;
                position: absolute;
                inset: 0;
                background: transparent !important;
            }}
            .status-pill {{
                position: absolute;
                top: 8px;
                left: 8px;
                display: inline-flex;
                align-items: center;
                gap: 7px;
                background: {cfg['pill_bg']};
                color: {cfg['pill_text']};
                padding: 5px 13px;
                border-radius: 999px;
                font-size: 12px;
                font-weight: 600;
                box-shadow: 0 4px 12px rgba(255, 90, 31, 0.08);
                border: 1px solid rgba(255, 107, 44, 0.22);
                z-index: 10;
            }}
            .dot {{
                width: 7px;
                height: 7px;
                border-radius: 50%;
                background: {cfg['dot']};
                animation: pulse 1.1s infinite alternate;
            }}
            @keyframes pulse {{
                from {{ opacity: 0.35; transform: scale(0.85); }}
                to {{ opacity: 1; transform: scale(1.2); }}
            }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    </head>
    <body>
        <div class="status-pill">
            <span class="dot"></span>
            <span>{cfg['label']}</span>
        </div>
        <div id="canvas-container"></div>

        <script>
            const container = document.getElementById('canvas-container');
            const scene = new THREE.Scene();

            const camera = new THREE.PerspectiveCamera(40, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(0, 1.8, 7.2);
            camera.lookAt(0, 0, 0);

            const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setClearColor(0x000000, 0);
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            container.appendChild(renderer.domElement);

            // Soft Studio Lighting
            const ambient = new THREE.AmbientLight(0xffffff, 0.9);
            scene.add(ambient);

            const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.95);
            dirLight1.position.set(5, 8, 6);
            scene.add(dirLight1);

            const dirLight2 = new THREE.DirectionalLight("{cfg['gear_main']}", 0.5);
            dirLight2.position.set(-5, -3, 4);
            scene.add(dirLight2);

            function createSmoothGear(radius, teeth, thickness, colorHex) {{
                const group = new THREE.Group();
                const mat = new THREE.MeshStandardMaterial({{
                    color: colorHex,
                    metalness: 0.25,
                    roughness: 0.3
                }});

                const discGeo = new THREE.CylinderGeometry(radius, radius, thickness, 36);
                discGeo.rotateX(Math.PI / 2);
                group.add(new THREE.Mesh(discGeo, mat));

                const hubGeo = new THREE.TorusGeometry(radius * 0.48, thickness * 0.36, 14, 28);
                group.add(new THREE.Mesh(hubGeo, mat));

                const toothW = (2 * Math.PI * radius) / (teeth * 2.15);
                const toothH = radius * 0.18;
                const toothGeo = new THREE.BoxGeometry(toothW, toothH, thickness * 0.92);

                for (let i = 0; i < teeth; i++) {{
                    const angle = (i / teeth) * Math.PI * 2;
                    const tooth = new THREE.Mesh(toothGeo, mat);
                    tooth.position.set(
                        Math.cos(angle) * (radius + toothH * 0.38),
                        Math.sin(angle) * (radius + toothH * 0.38),
                        0
                    );
                    tooth.rotation.z = angle - Math.PI / 2;
                    group.add(tooth);
                }}
                return group;
            }}

            const assembly = new THREE.Group();
            const sunGear = createSmoothGear(1.35, 16, 0.36, "{cfg['gear_main']}");
            const leftGear = createSmoothGear(0.85, 11, 0.34, "{cfg['gear_sub']}");
            leftGear.position.set(-2.3, 0.3, 0);

            const rightGear = createSmoothGear(0.85, 11, 0.34, "{cfg['gear_sub']}");
            rightGear.position.set(2.3, -0.3, 0);

            const ringGeo = new THREE.TorusGeometry(3.2, 0.025, 12, 64);
            const ringMat = new THREE.MeshBasicMaterial({{ color: "{cfg['gear_main']}", transparent: true, opacity: 0.3 }});
            const ring = new THREE.Mesh(ringGeo, ringMat);
            ring.rotation.x = Math.PI / 2.3;

            assembly.add(sunGear, leftGear, rightGear, ring);
            scene.add(assembly);

            const speed = {cfg['speed']};
            let t = 0;

            function animate() {{
                requestAnimationFrame(animate);
                t += speed;
                sunGear.rotation.z -= speed;
                leftGear.rotation.z += speed * 1.45;
                rightGear.rotation.z += speed * 1.45;
                assembly.rotation.y = Math.sin(t * 0.65) * 0.25;
                ring.rotation.z += speed * 0.7;
                renderer.render(scene, camera);
            }}
            animate();

            window.addEventListener('resize', () => {{
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=230)