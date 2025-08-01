/**
 * ContactPage component
 */

import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
`;

const ComingSoon = styled.div`
  font-size: 24px;
  color: #1e3c72;
  margin-bottom: 20px;
`;

const ContactPage: React.FC = () => {
  return (
    <Container>
      <ComingSoon>🚧 Contact Page - Coming Soon</ComingSoon>
      <p>This page will have a contact form and our contact information.</p>
    </Container>
  );
};

export default ContactPage;
