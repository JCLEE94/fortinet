// 네비게이션 바 강제 고정 스크립트
document.addEventListener('DOMContentLoaded', function() {
    console.log('네비게이션 고정 스크립트 시작');
    
    // 네비게이션 요소 찾기
    const navbar = document.getElementById('navbar') || document.querySelector('.modern-navbar');
    
    if (navbar) {
        console.log('네비게이션 바 발견, 강제 고정 적용');
        
        // 강제로 스타일 고정
        function forceNavbarPosition() {
            navbar.style.position = 'fixed';
            navbar.style.top = '0';
            navbar.style.left = '0';
            navbar.style.right = '0';
            navbar.style.zIndex = '9999';
            navbar.style.transform = 'none';
            navbar.style.animation = 'none';
            navbar.style.transition = 'background-color 0.3s ease';
            navbar.style.background = '#E50038';
            navbar.style.width = '100%';
            navbar.style.height = '60px';
        }
        
        // 즉시 적용
        forceNavbarPosition();
        
        // 0.1초마다 확인하여 다른 스크립트가 바꾸지 못하도록 방지
        setInterval(forceNavbarPosition, 100);
        
        // 스크롤 이벤트에서도 고정 유지
        window.addEventListener('scroll', function() {
            forceNavbarPosition();
        });
        
        // resize 이벤트에서도 고정 유지
        window.addEventListener('resize', function() {
            forceNavbarPosition();
        });
        
        console.log('네비게이션 고정 완료');
    } else {
        console.log('네비게이션 바를 찾을 수 없음');
    }
    
    // 모든 애니메이션 강제 중지
    const style = document.createElement('style');
    style.textContent = `
        .modern-navbar, #navbar {
            animation: none !important;
            transform: none !important;
            position: fixed !important;
            top: 0 !important;
            z-index: 9999 !important;
        }
    `;
    document.head.appendChild(style);
});

// 페이지 로드 후에도 한 번 더 확인
window.addEventListener('load', function() {
    setTimeout(function() {
        const navbar = document.getElementById('navbar') || document.querySelector('.modern-navbar');
        if (navbar) {
            navbar.style.position = 'fixed';
            navbar.style.top = '0';
            navbar.style.transform = 'none';
            navbar.style.animation = 'none';
            console.log('페이지 로드 후 네비게이션 재고정 완료');
        }
    }, 500);
});