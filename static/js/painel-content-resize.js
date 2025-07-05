// painel-content-resize.js
// Script para ajustar o painel principal conforme a sidebar abre/fecha

document.addEventListener('DOMContentLoaded', function() {
  const sidebar = document.getElementById('sidebar');
  const mainContent = document.getElementById('main-content-panel');
  const painelContent = document.getElementById('painel-content');
  const sidebarPanel = document.getElementById('sidebar-panel');
  const btn = document.getElementById('toggleSidebarBtn');
  if (!sidebar || !mainContent || !painelContent || !sidebarPanel || !btn) return;
  btn.addEventListener('click', function () {
    if (sidebar.style.transform === 'translateX(-100%)') {
      sidebarPanel.style.width = '0';
      painelContent.style.marginLeft = '0';
      painelContent.style.width = '100%';
    } else {
      sidebarPanel.style.width = '';
      painelContent.style.marginLeft = '';
      painelContent.style.width = '';
    }
  });
});
