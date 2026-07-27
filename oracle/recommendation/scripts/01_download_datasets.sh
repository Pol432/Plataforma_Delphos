#!/bin/bash

echo "=================================="
echo "DAO Prototype - Dataset Download"
echo "=================================="

cd /workspace/data/raw

# Dataset 1: Career Path Recommendations
echo ""
echo "Downloading Dataset 1: Career Path Recommendations..."
kaggle datasets download -d ahsanneural/career-path-recommendations-dataset --unzip
mv career-path-recommendations-dataset career_paths

# Dataset 2: AI Career Recommendation
echo ""
echo "Downloading Dataset 2: AI Career Recommendation..."
kaggle datasets download -d adilshamim8/ai-based-career-recommendation-system --unzip
mv ai-based-career-recommendation-system ai_career

# Dataset 3: Skill & Career Recommendation
echo ""
echo "Downloading Dataset 3: Skill & Career Recommendation..."
kaggle datasets download -d tea340yashjoshi/skill-and-career-recommendation-dataset --unzip
mv skill-and-career-recommendation-dataset skill_career

# Dataset 4: LinkedIn Job Postings (for company/industry data)
echo ""
echo "Downloading Dataset 4: LinkedIn Job Postings..."
kaggle datasets download -d arshkon/linkedin-job-postings --unzip
mv linkedin-job-postings linkedin

# Dataset 5: Data Science Salaries (for skill value estimation)
echo ""
echo "Downloading Dataset 5: Salary Data..."
kaggle datasets download -d arnabchaki/data-science-salaries-2023 --unzip
mv data-science-salaries-2023 salaries

echo ""
echo "=================================="
echo "Downloads Complete!"
echo "=================================="

# Show what we have
echo ""
echo "Downloaded datasets:"
ls -lh
