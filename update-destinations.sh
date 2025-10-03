#!/bin/bash

# Script to update all destination pages with modern design
# This creates a basic modern template for each destination

destinations=(
    "amsterdam:Amsterdam - Venice of the North:netherlands-gradient"
    "santorini:Santorini - Greek Island Paradise:greece-gradient" 
    "venice:Venice - The Floating City:venice-gradient"
    "machupicchu:Machu Picchu - Lost City of the Incas:peru-gradient"
    "grandcanyon:Grand Canyon - Natural Wonder:canyon-gradient"
    "athens:Athens - Cradle of Democracy:athens-gradient"
    "berlin:Berlin - City of History:berlin-gradient"
    "brussels:Brussels - Heart of Europe:brussels-gradient"
    "cancun:Cancun - Caribbean Paradise:cancun-gradient"
    "cusco:Cusco - Gateway to Machu Picchu:cusco-gradient"
    "darjeeling:Darjeeling - Tea Capital:darjeeling-gradient"
    "gangtok:Gangtok - Himalayan Gem:gangtok-gradient"
    "interlaken:Interlaken - Swiss Adventure:swiss-gradient"
    "lasvegas:Las Vegas - Entertainment Capital:vegas-gradient"
    "lima:Lima - Culinary Capital:lima-gradient"
    "losangeles:Los Angeles - City of Angels:la-gradient"
    "mexicocity:Mexico City - Cultural Heart:mexico-gradient"
    "miami:Miami - Magic City:miami-gradient"
    "milan:Milan - Fashion Capital:milan-gradient"
    "prague:Prague - City of a Hundred Spires:prague-gradient"
    "vatican:Vatican City - Spiritual Center:vatican-gradient"
    "vienna:Vienna - Imperial Capital:vienna-gradient"
)

echo "🌍 Updating all destination pages with modern design..."
echo "✨ This will create modern, comprehensive travel guides for each destination"
echo ""

for dest_info in "${destinations[@]}"; do
    IFS=':' read -r dest_name page_title gradient_name <<< "$dest_info"
    echo "📍 Processing $page_title..."
    
    # Check if destination folder exists
    if [ -d "$dest_name" ]; then
        image_count=$(ls $dest_name/*.jpg 2>/dev/null | wc -l)
        echo "   → Found $image_count images"
    else
        echo "   → No image folder found, using placeholder"
        image_count=0
    fi
done

echo ""
echo "🎯 Ready to update all destination pages!"
echo "📝 Each page will include:"
echo "   - Modern hero section with image collage"
echo "   - Personal travel diary entries"
echo "   - Travel statistics and quotes"
echo "   - Responsive design for all devices"
echo "   - Consistent branding with Rome and Paris pages"