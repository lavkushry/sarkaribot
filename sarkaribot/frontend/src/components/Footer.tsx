/**
 * Footer component for SarkariBot
 * Replicates SarkariExam.com footer design
 */

import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

const FooterContainer = styled.footer`
  background: #1e3c72;
  color: white;
  margin-top: 50px;
`;

const FooterContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px 20px;
`;

const FooterGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  margin-bottom: 30px;
`;

const FooterSection = styled.div`
  h3 {
    font-size: 18px;
    margin-bottom: 15px;
    color: #fff;
    font-weight: 600;
  }

  p {
    line-height: 1.6;
    margin-bottom: 15px;
    color: #e0e7ff;
  }
`;

const FooterLinks = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
  
  li {
    margin-bottom: 8px;
    
    a {
      color: #e0e7ff;
      text-decoration: none;
      font-size: 14px;
      transition: color 0.3s;
      
      &:hover {
        color: #fff;
        text-decoration: underline;
      }
    }
  }
`;

const SocialLinks = styled.div`
  display: flex;
  gap: 15px;
  margin-top: 15px;
`;

const SocialLink = styled.a`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  color: white;
  text-decoration: none;
  font-size: 18px;
  transition: all 0.3s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
  }
`;

const NewsletterForm = styled.form`
  display: flex;
  gap: 10px;
  margin-top: 15px;
  
  input {
    flex: 1;
    padding: 10px;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    
    &::placeholder {
      color: #999;
    }
  }
  
  button {
    background: #ff6b35;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: background 0.3s;
    
    &:hover {
      background: #e55a2b;
    }
  }
`;

const FooterBottom = styled.div`
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
  
  @media (max-width: 768px) {
    flex-direction: column;
    text-align: center;
  }
`;

const Copyright = styled.div`
  font-size: 14px;
  color: #e0e7ff;
`;

const BottomLinks = styled.div`
  display: flex;
  gap: 20px;
  
  a {
    color: #e0e7ff;
    text-decoration: none;
    font-size: 14px;
    
    &:hover {
      color: #fff;
      text-decoration: underline;
    }
  }
  
  @media (max-width: 768px) {
    flex-wrap: wrap;
    justify-content: center;
  }
`;

const Footer: React.FC = () => {
  const handleNewsletterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Newsletter subscription logic will be implemented later
    alert('Newsletter subscription coming soon!');
  };

  return (
    <FooterContainer>
      <FooterContent>
        <FooterGrid>
          {/* About Section */}
          <FooterSection>
            <h3>About SarkariBot</h3>
            <p>
              SarkariBot is your ultimate destination for government job notifications. 
              We provide latest updates on central and state government jobs, admit cards, 
              answer keys, and results.
            </p>
            <SocialLinks>
              <SocialLink href="#" aria-label="Facebook">📘</SocialLink>
              <SocialLink href="#" aria-label="Twitter">🐦</SocialLink>
              <SocialLink href="#" aria-label="Telegram">📱</SocialLink>
              <SocialLink href="#" aria-label="YouTube">📺</SocialLink>
              <SocialLink href="#" aria-label="Instagram">📷</SocialLink>
            </SocialLinks>
          </FooterSection>

          {/* Quick Links */}
          <FooterSection>
            <h3>Quick Links</h3>
            <FooterLinks>
              <li><Link to="/jobs/latest">Latest Jobs</Link></li>
              <li><Link to="/jobs/admit-card">Admit Card</Link></li>
              <li><Link to="/jobs/answer-key">Answer Key</Link></li>
              <li><Link to="/jobs/result">Result</Link></li>
              <li><Link to="/categories">All Categories</Link></li>
              <li><Link to="/job-alerts">Job Alerts</Link></li>
              <li><Link to="/syllabus">Syllabus</Link></li>
              <li><Link to="/previous-papers">Previous Papers</Link></li>
            </FooterLinks>
          </FooterSection>

          {/* Categories */}
          <FooterSection>
            <h3>Popular Categories</h3>
            <FooterLinks>
              <li><Link to="/category/banking">Banking</Link></li>
              <li><Link to="/category/ssc">SSC</Link></li>
              <li><Link to="/category/railway">Railway</Link></li>
              <li><Link to="/category/defense">Defense</Link></li>
              <li><Link to="/category/upsc">UPSC</Link></li>
              <li><Link to="/category/teaching">Teaching</Link></li>
              <li><Link to="/category/police">Police</Link></li>
              <li><Link to="/category/psu">PSU</Link></li>
            </FooterLinks>
          </FooterSection>

          {/* Newsletter */}
          <FooterSection>
            <h3>Stay Updated</h3>
            <p>
              Subscribe to our newsletter and get the latest government job 
              notifications directly in your inbox.
            </p>
            <NewsletterForm onSubmit={handleNewsletterSubmit}>
              <input 
                type="email" 
                placeholder="Enter your email" 
                required 
              />
              <button type="submit">Subscribe</button>
            </NewsletterForm>
          </FooterSection>
        </FooterGrid>

        <FooterBottom>
          <Copyright>
            © 2024 SarkariBot. All rights reserved. | Made with ❤️ for job seekers
          </Copyright>
          
          <BottomLinks>
            <Link to="/about">About Us</Link>
            <Link to="/contact">Contact</Link>
            <Link to="/privacy">Privacy Policy</Link>
            <Link to="/terms">Terms of Service</Link>
            <Link to="/disclaimer">Disclaimer</Link>
          </BottomLinks>
        </FooterBottom>
      </FooterContent>
    </FooterContainer>
  );
};

export default Footer;
