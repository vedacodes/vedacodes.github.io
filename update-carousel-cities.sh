#!/bin/bash

# Cities that need carousel updates
cities=("vienna" "interlaken" "berlin" "athens" "brussels")

for city in "${cities[@]}"; do
    echo "Updating $city-page.html with carousel functionality..."
    
    # Add carousel CSS after the image gallery styles
    sed -i '/\.gallery-item:hover \.image-overlay {/,/opacity: 1;/c\
        .carousel-container {\
            position: relative;\
            overflow: hidden;\
            border-radius: var(--border-radius) var(--border-radius) 0 0;\
        }\
\
        .carousel-wrapper {\
            position: relative;\
            width: 100%;\
            min-height: 200px;\
            overflow: hidden;\
            display: flex;\
            transition: transform 0.3s ease;\
        }\
\
        .carousel-slide {\
            min-width: 100%;\
            position: relative;\
        }\
\
        .carousel-slide img {\
            width: 100%;\
            height: auto;\
            display: block;\
            border-radius: var(--border-radius) var(--border-radius) 0 0;\
            object-fit: cover;\
        }\
\
        .carousel-nav {\
            position: absolute;\
            top: 50%;\
            transform: translateY(-50%);\
            background: rgba(255, 255, 255, 0.9);\
            border: none;\
            width: 40px;\
            height: 40px;\
            border-radius: 50%;\
            cursor: pointer;\
            display: flex;\
            align-items: center;\
            justify-content: center;\
            font-size: 1.2rem;\
            color: var(--text-primary);\
            transition: var(--transition);\
            z-index: 10;\
            backdrop-filter: blur(10px);\
        }\
\
        .carousel-nav:hover {\
            background: rgba(255, 255, 255, 1);\
            transform: translateY(-50%) scale(1.1);\
        }\
\
        .carousel-prev {\
            left: 15px;\
        }\
\
        .carousel-next {\
            right: 15px;\
        }\
\
        .carousel-indicators {\
            position: absolute;\
            bottom: 15px;\
            left: 50%;\
            transform: translateX(-50%);\
            display: flex;\
            gap: 8px;\
            z-index: 10;\
        }\
\
        .carousel-indicator {\
            width: 8px;\
            height: 8px;\
            border-radius: 50%;\
            background: rgba(255, 255, 255, 0.5);\
            cursor: pointer;\
            transition: var(--transition);\
        }\
\
        .carousel-indicator.active {\
            background: rgba(255, 255, 255, 1);\
            transform: scale(1.2);\
        }\
\
        .carousel-counter {\
            position: absolute;\
            top: 15px;\
            right: 15px;\
            background: rgba(0, 0, 0, 0.7);\
            color: white;\
            padding: 5px 10px;\
            border-radius: 15px;\
            font-size: 0.85rem;\
            font-weight: 500;\
            z-index: 10;\
        }' "$city-page.html"
    
done

echo "All pages updated with carousel CSS!"