/**
 * NotFoundPage component - 404 error page
 */

import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 60px 20px;
  text-align: center;
  min-height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
`;

const ErrorCode = styled.h1`
  font-size: 120px;
  color: #1e3c72;
  margin: 0;
  font-weight: bold;
`;

const ErrorMessage = styled.h2`
  font-size: 32px;
  color: #333;
  margin: 20px 0;
  font-weight: 600;
`;

const ErrorDescription = styled.p`
  font-size: 18px;
  color: #666;
  margin-bottom: 40px;
  line-height: 1.6;
`;

const HomeButton = styled(Link)`
  background: #1e3c72;
  color: white;
  padding: 15px 30px;
  border-radius: 25px;
  text-decoration: none;
  font-size: 16px;
  font-weight: 500;
  transition: background-color 0.3s;
  
  &:hover {
    background: #2a5298;
  }
`;

const NotFoundPage: React.FC = () => {
  return (
    <Container>
      <ErrorCode>404</ErrorCode>
      <ErrorMessage>Page Not Found</ErrorMessage>
      <ErrorDescription>
        Sorry, the page you are looking for doesn't exist or has been moved. 
        Let's get you back to finding your dream government job!
      </ErrorDescription>
      <HomeButton to="/">
        🏠 Go Back Home
      </HomeButton>
    </Container>
  );
};

export default NotFoundPage;
