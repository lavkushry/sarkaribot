/**
 * AboutPage component
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

const AboutPage: React.FC = () => {
  return (
    <Container>
      <ComingSoon>🚧 About Page - Coming Soon</ComingSoon>
      <p>This page will contain information about SarkariBot and our mission.</p>
    </Container>
  );
};

export default AboutPage;
