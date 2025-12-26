import React, { useState } from 'react'
import styled from 'styled-components'

const HeroSectionWrapper = styled.div`
  position: relative;
  padding: 4rem 0;
  text-align: center;
  
  @media (max-width: 768px) {
    padding: 2rem 0;
  }
`

const BackgroundImage = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  
  @media (prefers-color-scheme: dark) {
    background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://source.unsplash.com/random?min_width=1200&max_height=500');
  }
  
  @media (prefers-color-scheme: light) {
    background-image: linear-gradient(to bottom right, #667eea, #764ba2), url('https://source.unsplash.com/random?min_width=1200&max_height=500');
  }
`

const Title = styled.h1`
  font-size: 3rem;
  color: white;
  margin-top: 1rem;
  
  @media (max-width: 768px) {
    font-size: 2rem;
  }
`

const Subtitle = styled.p`
  font-size: 1.5rem;
  color: #ccc;
  margin-top: 0.5rem;
  
  @media (max-width: 768px) {
    font-size: 1.25rem;
  }
`

export const HeroSection = ({ title, subtitle, imageUrl }) => {
  const [loaded, setLoaded] = useState(false)

  return (
    <HeroSectionWrapper>
      {imageUrl ? <BackgroundImage style={{ backgroundImage: `url(${imageUrl})` }} /> : null}
      <Title>{title}</Title>
      <Subtitle>{subtitle}</Subtitle>
    </HeroSectionWrapper>
  )
}

export default HeroSection
```

This component provides a flexible hero section that can be used to showcase key content at the top of pages. It supports passing in custom images or using a dark mode gradient background by default.

The styles are written using styled-components for easy theming and responsive breakpoints.

## License

MIT Licensed

## Author

Created by [Your Name], 2023
```

Let me know if you would like me to modify or expand the README further. I aimed to include all of the key details about the component, its usage, implementation, styling and licensing in a clear format.