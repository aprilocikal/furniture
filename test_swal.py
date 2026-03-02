import streamlit as st
import streamlit.components.v1 as components

st.title("Test Sweetalert")
if st.button("Click Me"):
    components.html("""
        <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
        <script>
            window.parent.eval(`
                if (!window.Swal) {
                    let script = document.createElement('script');
                    script.src = 'https://cdn.jsdelivr.net/npm/sweetalert2@11';
                    document.head.appendChild(script);
                }
            `);
            setTimeout(() => {
                window.parent.Swal.fire({
                    title: 'Sukses!',
                    text: 'Data berhasil ditambahkan',
                    icon: 'success'
                });
            }, 200);
        </script>
    """, height=0, width=0)
