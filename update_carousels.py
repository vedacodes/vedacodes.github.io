#!/usr/bin/env python3

import re
from collections import defaultdict
import os

def parse_image_mapping():
    """Parse the image-mapping.txt file to get city image groups"""
    city_images = {}
    current_city = None
    
    with open('image-mapping.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a city header
            if line.endswith(':'):
                current_city = line[:-1]
                city_images[current_city] = defaultdict(list)
                continue
            
            # Parse image mapping
            if '=' in line and current_city:
                parts = line.split('=', 1)
                if len(parts) == 2:
                    image_file = parts[0].strip()
                    description = parts[1].strip()
                    city_images[current_city][description].append(image_file)
    
    return city_images

def generate_carousel_gallery(city, image_groups):
    """Generate the gallery HTML with carousels for a city"""
    gallery_html = []
    carousel_ids = []
    
    for description, images in image_groups.items():
        if len(images) > 1:
            # Create carousel
            # Clean up description for carousel ID
            clean_desc = description.lower()
            clean_desc = clean_desc.replace(' ', '-').replace("'", '').replace('"', '')
            clean_desc = clean_desc.replace('(', '').replace(')', '').replace(',', '')
            clean_desc = clean_desc.replace('.', '').replace('!', '').replace('?', '')
            clean_desc = clean_desc.replace(':', '').replace(';', '').replace('&', 'and')
            carousel_id = f"{clean_desc}-carousel"
            carousel_ids.append(carousel_id)
            
            slides_html = []
            for i, image in enumerate(images):
                active_class = "active" if i == 0 else ""
                slides_html.append(f'                                <div class="carousel-slide {active_class}">')
                slides_html.append(f'                                    <img src="{city}/{image}" alt="{description} view {i+1}" loading="lazy">')
                slides_html.append(f'                                </div>')
            
            gallery_html.extend([
                f'                <!-- {description} Carousel -->',
                f'                <div class="gallery-item">',
                f'                    <div class="gallery-image-container">',
                f'                        <div class="carousel-container">',
                f'                            <div class="carousel-wrapper" id="{carousel_id}">',
                *slides_html,
                f'                            </div>',
                f'                            <button class="carousel-nav carousel-prev" onclick="moveCarousel(\'{carousel_id}\', -1)">‹</button>',
                f'                            <button class="carousel-nav carousel-next" onclick="moveCarousel(\'{carousel_id}\', 1)">›</button>',
                f'                            <div class="carousel-indicators" id="{carousel_id}-indicators"></div>',
                f'                            <div class="carousel-counter" id="{carousel_id}-counter">1 / {len(images)}</div>',
                f'                        </div>',
                f'                    </div>',
                f'                    <div class="gallery-caption">',
                f'                        <h3>{description}</h3>',
                f'                        <p>Experiencing the beauty and magic of {description} was truly unforgettable. Each moment captured here tells a story of wonder, discovery, and the incredible journey that travel brings to our lives.</p>',
                f'                    </div>',
                f'                </div>',
                f''
            ])
        else:
            # Single image
            image = images[0]
            gallery_html.extend([
                f'                <!-- {description} -->',
                f'                <div class="gallery-item">',
                f'                    <div class="gallery-image-container">',
                f'                        <img src="{city}/{image}" alt="{description}" class="gallery-image" loading="lazy">',
                f'                    </div>',
                f'                    <div class="gallery-caption">',
                f'                        <h3>{description}</h3>',
                f'                        <p>Experiencing the beauty and magic of {description} was truly unforgettable. This moment captured here tells a story of wonder, discovery, and the incredible journey that travel brings to our lives.</p>',
                f'                    </div>',
                f'                </div>',
                f''
            ])
    
    return '\n'.join(gallery_html), carousel_ids

def generate_carousel_js(carousel_ids):
    """Generate the JavaScript for carousel functionality"""
    if not carousel_ids:
        return ""
    
    js_carousel_ids = "'" + "',\n                '".join(carousel_ids) + "'"
    
    return f"""
        // Carousel functionality
        const carousels = {{}};

        function initCarousel(carouselId) {{
            const wrapper = document.getElementById(carouselId);
            if (!wrapper) return;

            const slides = wrapper.querySelectorAll('.carousel-slide');
            const indicatorsContainer = document.getElementById(carouselId + '-indicators');
            const counter = document.getElementById(carouselId + '-counter');
            
            carousels[carouselId] = {{
                currentSlide: 0,
                totalSlides: slides.length,
                wrapper: wrapper,
                slides: slides,
                indicators: [],
                counter: counter
            }};

            // Create indicators
            if (indicatorsContainer && slides.length > 1) {{
                for (let i = 0; i < slides.length; i++) {{
                    const indicator = document.createElement('div');
                    indicator.className = 'carousel-indicator';
                    if (i === 0) indicator.classList.add('active');
                    indicator.addEventListener('click', () => goToSlide(carouselId, i));
                    indicatorsContainer.appendChild(indicator);
                    carousels[carouselId].indicators.push(indicator);
                }}
            }}

            // Set initial position
            updateCarousel(carouselId);
        }}

        function moveCarousel(carouselId, direction) {{
            const carousel = carousels[carouselId];
            if (!carousel) return;

            carousel.currentSlide += direction;
            
            if (carousel.currentSlide >= carousel.totalSlides) {{
                carousel.currentSlide = 0;
            }} else if (carousel.currentSlide < 0) {{
                carousel.currentSlide = carousel.totalSlides - 1;
            }}

            updateCarousel(carouselId);
        }}

        function goToSlide(carouselId, slideIndex) {{
            const carousel = carousels[carouselId];
            if (!carousel) return;

            carousel.currentSlide = slideIndex;
            updateCarousel(carouselId);
        }}

        function updateCarousel(carouselId) {{
            const carousel = carousels[carouselId];
            if (!carousel) return;

            // Update slides
            carousel.slides.forEach((slide, index) => {{
                slide.classList.toggle('active', index === carousel.currentSlide);
            }});

            // Update wrapper position
            const translateX = -carousel.currentSlide * 100;
            carousel.wrapper.style.transform = `translateX(${{translateX}}%)`;

            // Update indicators
            carousel.indicators.forEach((indicator, index) => {{
                indicator.classList.toggle('active', index === carousel.currentSlide);
            }});

            // Update counter
            if (carousel.counter) {{
                carousel.counter.textContent = `${{carousel.currentSlide + 1}} / ${{carousel.totalSlides}}`;
            }}
        }}

        // Initialize all carousels
        document.addEventListener('DOMContentLoaded', () => {{
            const carouselIds = [
                {js_carousel_ids}
            ];

            carouselIds.forEach(id => {{
                initCarousel(id);
            }});
        }});"""

def main():
    # Parse image mapping
    city_images = parse_image_mapping()
    
    print("Cities found in image mapping:")
    for city in city_images.keys():
        print(f"- {city}")
    
    print("\nGenerate carousel updates for which cities? (comma-separated, or 'all' for all cities)")
    user_input = input().strip()
    
    if user_input.lower() == 'all':
        cities_to_update = list(city_images.keys())
    else:
        cities_to_update = [city.strip() for city in user_input.split(',')]
    
    for city in cities_to_update:
        if city not in city_images:
            print(f"Warning: City '{city}' not found in image mapping")
            continue
        
        print(f"\nProcessing {city}...")
        
        # Check if page exists
        page_file = f"{city}-page.html"
        if not os.path.exists(page_file):
            print(f"Warning: {page_file} does not exist")
            continue
        
        # Generate gallery HTML and carousel JS
        gallery_html, carousel_ids = generate_carousel_gallery(city, city_images[city])
        carousel_js = generate_carousel_js(carousel_ids)
        
        # Print the generated content for manual copying
        print(f"\n{'='*50}")
        print(f"GALLERY HTML FOR {city.upper()}:")
        print(f"{'='*50}")
        print(gallery_html)
        
        if carousel_js:
            print(f"\n{'='*50}")
            print(f"CAROUSEL JAVASCRIPT FOR {city.upper()}:")
            print(f"{'='*50}")
            print(carousel_js)
        
        print(f"\n{'='*50}")
        print(f"END OF {city.upper()} UPDATE")
        print(f"{'='*50}")

if __name__ == "__main__":
    main()