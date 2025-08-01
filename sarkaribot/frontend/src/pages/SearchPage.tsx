/**
 * SearchPage component - Search results
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

const SearchPage: React.FC = () => {
  return (
    <Container>
      <ComingSoon>🚧 Search Page - Coming Soon</ComingSoon>
      <p>This page will show search results for job queries.</p>
    </Container>
  );
};

export default SearchPage;
