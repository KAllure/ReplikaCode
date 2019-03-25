FROM 656397365169.dkr.ecr.us-west-1.amazonaws.com/luka/ml-gpu:2.1

# Copy sources
COPY src /root/cakechat-internal

# Install dependencies
RUN pip3 --no-cache-dir install -r /root/cakechat-internal/requirements.txt --process-dependency-links

# Clean keys
RUN rm -R /root/.ssh/

WORKDIR /root/cakechat-internal/bin
CMD ["/bin/bash"]
