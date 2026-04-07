#!/bin/bash
set -e
BUCKET="bibliometria-turismo-multivariado"
echo "=== Rendering Quarto ==="
quarto render quarto/
echo "=== Syncing to S3 ==="
aws s3 sync quarto/_site/ s3://$BUCKET/ --delete --cache-control "max-age=3600" --exclude ".git/*"
echo "=== Published ==="
echo "URL: http://$BUCKET.s3-website.eu-west-3.amazonaws.com"
