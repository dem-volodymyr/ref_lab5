#!/bin/bash

set -e

echo "Running Product Service tests..."
cd product_service && pytest && cd ..

echo "Running Order Service tests..."
cd /Users/demchyshynvolodymyr/PycharmProjects/ref_lab5/order_service && pytest && cd ..

echo "Running Payment Service tests..."
cd /Users/demchyshynvolodymyr/PycharmProjects/ref_lab5/payment_service && pytest && cd ..

echo "All tests completed!" 