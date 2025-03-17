import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  FormControl, 
  FormLabel, 
  Input, 
  Select, 
  Textarea, 
  VStack, 
  Heading, 
  Text, 
  useToast,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Container 
} from '@chakra-ui/react';
import { API_BASE_URL } from '../../config';

/**
 * Form component for patients to request new healthcare providers
 * to be added to the HealthData Gateway platform
 */
const PatientRequestForm = ({ token }) => {
  const [formData, setFormData] = useState({
    provider_name: '',
    provider_type: 'hospital',
    provider_website: '',
    provider_location: '',
    reason: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const toast = useToast();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/provider-registry/patient/request-provider`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          requested_by: localStorage.getItem('userId') || 'anonymous'
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to submit request');
      }
      
      const data = await response.json();
      setSubmitSuccess(true);
      toast({
        title: 'Request submitted successfully!',
        description: 'We\'ll notify you when this provider is available.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
      // Reset form after successful submission
      setFormData({
        provider_name: '',
        provider_type: 'hospital',
        provider_website: '',
        provider_location: '',
        reason: ''
      });
      
    } catch (error) {
      toast({
        title: 'Error submitting request',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Container maxW="container.md" p={5}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading as="h1" size="xl">Request a New Provider</Heading>
          <Text mt={2}>
            Can't find your healthcare provider? Submit a request to add them to our platform.
          </Text>
        </Box>
        
        {submitSuccess && (
          <Alert
            status="success"
            variant="subtle"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            textAlign="center"
            borderRadius="md"
            p={4}
          >
            <AlertIcon boxSize="40px" mr={0} />
            <AlertTitle mt={4} mb={1} fontSize="lg">
              Request Submitted!
            </AlertTitle>
            <AlertDescription maxWidth="sm">
              Thank you for your request. Our team will review it and reach out to the provider.
              You'll be notified when this provider becomes available on our platform.
            </AlertDescription>
          </Alert>
        )}
        
        <Box as="form" onSubmit={handleSubmit} borderWidth="1px" borderRadius="lg" p={6} bg="white" shadow="md">
          <VStack spacing={4} align="stretch">
            <FormControl isRequired>
              <FormLabel>Provider Name</FormLabel>
              <Input 
                name="provider_name" 
                value={formData.provider_name} 
                onChange={handleChange}
                placeholder="e.g., General Hospital, CVS Pharmacy, Fitbit"
              />
            </FormControl>
            
            <FormControl isRequired>
              <FormLabel>Provider Type</FormLabel>
              <Select name="provider_type" value={formData.provider_type} onChange={handleChange}>
                <option value="hospital">Hospital</option>
                <option value="pharmacy">Pharmacy</option>
                <option value="wearable">Wearable Device</option>
                <option value="lab">Laboratory</option>
                <option value="clinic">Clinic</option>
                <option value="other">Other</option>
              </Select>
            </FormControl>
            
            <FormControl>
              <FormLabel>Website (if known)</FormLabel>
              <Input 
                name="provider_website" 
                value={formData.provider_website} 
                onChange={handleChange}
                placeholder="https://www.example.com"
              />
            </FormControl>
            
            <FormControl>
              <FormLabel>Location/Address</FormLabel>
              <Input 
                name="provider_location" 
                value={formData.provider_location} 
                onChange={handleChange}
                placeholder="City, State or Full Address"
              />
            </FormControl>
            
            <FormControl>
              <FormLabel>Why do you want this provider added?</FormLabel>
              <Textarea 
                name="reason" 
                value={formData.reason} 
                onChange={handleChange}
                placeholder="Tell us why this provider would be valuable to you..."
                rows={4}
              />
            </FormControl>
            
            <Button 
              type="submit" 
              colorScheme="blue" 
              size="lg" 
              width="full"
              isLoading={isSubmitting}
              loadingText="Submitting"
              mt={4}
            >
              Submit Request
            </Button>
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
};

export default PatientRequestForm;
