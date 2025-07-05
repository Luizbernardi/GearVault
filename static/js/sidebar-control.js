
(function() {
  let isSidebarOpen = true;
  document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const button = document.getElementById('toggleSidebarBtn');
    const mainContent = document.querySelector('.container-fluid');
    if (!sidebar || !button || !mainContent) return;
    button.addEventListener('click', function () {
      isSidebarOpen = !isSidebarOpen;
      if (isSidebarOpen) {
        sidebar.style.transform = 'translateX(0)';
        button.style.left = '260px';
        mainContent.style.marginLeft = '';
        mainContent.style.marginRight = '';
        mainContent.style.maxWidth = '';
        mainContent.style.overflowX = '';
        document.body.classList.remove('sidebar-closed');
      } else {
        sidebar.style.transform = 'translateX(-100%)';
        button.style.left = '10px';
        mainContent.style.marginLeft = '70px';
        mainContent.style.maxWidth = `calc(100vw - 85px)`;
        mainContent.style.overflowX = 'hidden';
        document.body.classList.add('sidebar-closed');
      }
    });
  });
})();
