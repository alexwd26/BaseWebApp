"use client";
import React from 'react';
import styles from './PromotionalBanner.module.css';

const PromotionalBanner = () => {
  return (
    <div className={styles.bannerContainer}>
      <div className={styles.promotionalText}>
        Ofertas Especiais 🔥
      </div>
      <div className={styles.accentBar} />
    </div>
  );
};

export default PromotionalBanner;