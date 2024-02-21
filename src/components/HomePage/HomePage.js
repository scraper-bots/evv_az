// HomePage.js

import React from 'react';
import styles from './HomePage.module.css'; // Import styles from module

const HomePage = () => {
  return (
    <div className={styles.homeContainer}> {/* Use className from module */}
      <h1>Welcome to our store!</h1>
      <p>Explore our amazing products</p>
    </div>
  );
}

export default HomePage;
