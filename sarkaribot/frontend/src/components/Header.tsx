/**
 * Header component for SarkariBot
 * Replicates SarkariExam.com navigation structure
 */

import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';

const HeaderContainer = styled.header`
  background: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
`;

const TopBar = styled.div`
  background: #1e3c72;
  color: white;
  padding: 8px 0;
  font-size: 13px;
`;

const TopBarContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const TopBarLinks = styled.div`
  display: flex;
  gap: 20px;
  
  a {
    color: white;
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;

const MainHeader = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled(Link)`
  font-size: 28px;
  font-weight: bold;
  color: #1e3c72;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 10px;
  
  &:hover {
    color: #2a5298;
  }
`;

const LogoIcon = styled.div`
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #1e3c72, #2a5298);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 18px;
`;

const SearchContainer = styled.div`
  flex: 1;
  max-width: 500px;
  margin: 0 30px;
  position: relative;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 12px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 25px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s;
  
  &:focus {
    border-color: #1e3c72;
  }
  
  &::placeholder {
    color: #999;
  }
`;

const SearchButton = styled.button`
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  background: #1e3c72;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  
  &:hover {
    background: #2a5298;
  }
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 15px;
  align-items: center;
`;

const AlertButton = styled.button`
  background: #ff6b35;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  
  &:hover {
    background: #e55a2b;
  }
`;

const Navigation = styled.nav`
  background: #f8f9fa;
  border-top: 1px solid #e0e0e0;
`;

const NavContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
`;

const NavList = styled.ul`
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 0;
`;

const NavItem = styled.li<{ active?: boolean }>`
  position: relative;
  
  a {
    display: block;
    padding: 15px 20px;
    color: ${props => props.active ? '#1e3c72' : '#333'};
    text-decoration: none;
    font-weight: ${props => props.active ? '600' : '500'};
    font-size: 14px;
    border-bottom: 3px solid ${props => props.active ? '#1e3c72' : 'transparent'};
    transition: all 0.3s;
    
    &:hover {
      color: #1e3c72;
      background: #fff;
    }
  }
`;

const MobileMenuButton = styled.button`
  display: none;
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #333;
  
  @media (max-width: 768px) {
    display: block;
  }
`;

const MobileNavigation = styled.div<{ isOpen: boolean }>`
  display: ${props => props.isOpen ? 'block' : 'none'};
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  background: white;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  z-index: 999;
  
  @media (min-width: 769px) {
    display: none;
  }
`;

const MobileNavList = styled.ul`
  list-style: none;
  margin: 0;
  padding: 0;
  
  li {
    border-bottom: 1px solid #e0e0e0;
    
    a {
      display: block;
      padding: 15px 20px;
      color: #333;
      text-decoration: none;
      
      &:hover {
        background: #f8f9fa;
        color: #1e3c72;
      }
    }
  }
`;

interface HeaderProps {
  className?: string;
}

const Header: React.FC<HeaderProps> = ({ className }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const navigationItems = [
    { label: 'Home', path: '/', exact: true },
    { label: 'Latest Jobs', path: '/jobs/latest' },
    { label: 'Admit Card', path: '/jobs/admit-card' },
    { label: 'Answer Key', path: '/jobs/answer-key' },
    { label: 'Result', path: '/jobs/result' },
    { label: 'Categories', path: '/categories' },
    { label: 'About', path: '/about' },
    { label: 'Contact', path: '/contact' },
  ];

  const isActiveRoute = (path: string, exact: boolean = false) => {
    if (exact) {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleJobAlert = () => {
    navigate('/job-alerts');
  };

  useEffect(() => {
    // Close mobile menu when route changes
    setIsMobileMenuOpen(false);
  }, [location]);

  useEffect(() => {
    // Handle body scroll when mobile menu is open
    if (isMobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isMobileMenuOpen]);

  return (
    <HeaderContainer className={className}>
      {/* Top bar with utility links */}
      <TopBar>
        <TopBarContent>
          <div>📧 Get Latest Job Updates | 📱 Download App</div>
          <TopBarLinks>
            <Link to="/newsletter">Newsletter</Link>
            <Link to="/job-alerts">Job Alerts</Link>
            <Link to="/syllabus">Syllabus</Link>
          </TopBarLinks>
        </TopBarContent>
      </TopBar>

      {/* Main header with logo and search */}
      <MainHeader>
        <Logo to="/">
          <LogoIcon>SB</LogoIcon>
          <div>
            <div>SarkariBot</div>
            <div style={{ fontSize: '12px', fontWeight: 'normal', color: '#666' }}>
              Government Jobs Portal
            </div>
          </div>
        </Logo>

        <SearchContainer>
          <form onSubmit={handleSearch}>
            <SearchInput
              type="text"
              placeholder="Search for government jobs, departments, locations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <SearchButton type="submit">
              🔍 Search
            </SearchButton>
          </form>
        </SearchContainer>

        <ActionButtons>
          <AlertButton onClick={handleJobAlert}>
            🔔 Job Alert
          </AlertButton>
          
          <MobileMenuButton onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
            ☰
          </MobileMenuButton>
        </ActionButtons>
      </MainHeader>

      {/* Navigation menu */}
      <Navigation>
        <NavContent>
          <NavList style={{ display: isMobileMenuOpen ? 'none' : 'flex' }}>
            {navigationItems.map((item) => (
              <NavItem
                key={item.path}
                active={isActiveRoute(item.path, item.exact)}
              >
                <Link to={item.path}>{item.label}</Link>
              </NavItem>
            ))}
          </NavList>
        </NavContent>

        {/* Mobile navigation */}
        <MobileNavigation isOpen={isMobileMenuOpen}>
          <MobileNavList>
            {navigationItems.map((item) => (
              <li key={item.path}>
                <Link to={item.path}>{item.label}</Link>
              </li>
            ))}
          </MobileNavList>
        </MobileNavigation>
      </Navigation>
    </HeaderContainer>
  );
};

export default Header;
