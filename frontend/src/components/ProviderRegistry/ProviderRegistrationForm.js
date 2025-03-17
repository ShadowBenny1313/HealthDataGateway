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
  Checkbox,
  Divider,
  Grid,
  GridItem,
  Container,
  Stack
} from '@chakra-ui/react';
import { API_BASE_URL } from '../../config';

/**
 * Form component for healthcare providers to register themselves
 * on the HealthData Gateway platform
 */
const ProviderRegistrationForm = ({ token }) => {
  const [formData, setFormData] = useState({
    name: '',
    type: 'hospital',
    description: '',
    website: '',
    logo_url: '',
    contact: {
      name: '',
      title: '',
      email: '',
      phone: ''
    },
    integration_info: {
      api_documentation: '',
      requires_oauth: false,
      supports_fhir: false,
      api_specifications: {},
      testing_credentials: {}
    },
    notes: ''
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const toast = useToast();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (name.includes('.')) {
      // Handle nested fields (e.g., contact.name)
      const [parent, child] = name.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: type === 'checkbox' ? checked : value
        }
      }));
    } else {
      // Handle top-level fields
      setFormData(prev => ({
        ...prev,
        [name]: type === 'checkbox' ? checked : value
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // Prepare submission data
      const submissionData = {
        ...formData,
        submitted_by: localStorage.getItem('providerId') || 'provider_representative'
      };
      
      const response = await fetch(`${API_BASE_URL}/api/provider-registry/provider/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(submissionData)
      });
      
      if (!response.ok) {
        throw new Error('Failed to submit registration');
      }
      
      const data = await response.json();
      setSubmitSuccess(true);
      toast({
        title: 'Registration submitted successfully!',
        description: 'We\'ll review your application and contact you soon.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
    } catch (error) {
      toast({
        title: 'Error submitting registration',
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
    <Container maxW="container.lg" p={5}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading as="h1" size="xl">Provider Registration</Heading>
          <Text mt={2}>
            Register your healthcare organization to integrate with the HealthData Gateway platform.
          </Text>
        </Box>
        
        {submitSuccess && (
          <Alert
            status="success"
            variant="subtle"
            borderRadius="md"
            p={4}
          >
            <AlertIcon />
            <Stack>
              <Text fontWeight="bold">Registration Submitted!</Text>
              <Text>
                Thank you for your interest in joining HealthData Gateway. Our team will review 
                your application and contact you to discuss the next steps in the integration process.
              </Text>
            </Stack>
          </Alert>
        )}
        
        <Box as="form" onSubmit={handleSubmit} borderWidth="1px" borderRadius="lg" p={6} bg="white" shadow="md">
          <VStack spacing={6} align="stretch">
            <Heading as="h3" size="md">Organization Information</Heading>
            
            <Grid templateColumns="repeat(2, 1fr)" gap={6}>
              <GridItem colSpan={[2, 1]}>
                <FormControl isRequired>
                  <FormLabel>Organization Name</FormLabel>
                  <Input 
                    name="name" 
                    value={formData.name} 
                    onChange={handleChange}
                    placeholder="Full legal name of your organization"
                  />
                </FormControl>
              </GridItem>
              
              <GridItem colSpan={[2, 1]}>
                <FormControl isRequired>
                  <FormLabel>Organization Type</FormLabel>
                  <Select name="type" value={formData.type} onChange={handleChange}>
                    <option value="hospital">Hospital System</option>
                    <option value="pharmacy">Pharmacy</option>
                    <option value="wearable">Wearable/Health Tech</option>
                    <option value="lab">Laboratory</option>
                    <option value="clinic">Clinic</option>
                    <option value="other">Other</option>
                  </Select>
                </FormControl>
              </GridItem>
            </Grid>
            
            <FormControl>
              <FormLabel>Description</FormLabel>
              <Textarea 
                name="description" 
                value={formData.description} 
                onChange={handleChange}
                placeholder="Brief description of your organization and services"
                rows={3}
              />
            </FormControl>
            
            <Grid templateColumns="repeat(2, 1fr)" gap={6}>
              <GridItem colSpan={[2, 1]}>
                <FormControl>
                  <FormLabel>Website</FormLabel>
                  <Input 
                    name="website" 
                    value={formData.website} 
                    onChange={handleChange}
                    placeholder="https://www.example.com"
                  />
                </FormControl>
              </GridItem>
              
              <GridItem colSpan={[2, 1]}>
                <FormControl>
                  <FormLabel>Logo URL</FormLabel>
                  <Input 
                    name="logo_url" 
                    value={formData.logo_url} 
                    onChange={handleChange}
                    placeholder="https://www.example.com/logo.png"
                  />
                </FormControl>
              </GridItem>
            </Grid>
            
            <Divider />
            
            <Heading as="h3" size="md">Contact Information</Heading>
            
            <Grid templateColumns="repeat(2, 1fr)" gap={6}>
              <GridItem colSpan={[2, 1]}>
                <FormControl isRequired>
                  <FormLabel>Contact Name</FormLabel>
                  <Input 
                    name="contact.name" 
                    value={formData.contact.name} 
                    onChange={handleChange}
                    placeholder="Full name of primary contact"
                  />
                </FormControl>
              </GridItem>
              
              <GridItem colSpan={[2, 1]}>
                <FormControl>
                  <FormLabel>Title/Position</FormLabel>
                  <Input 
                    name="contact.title" 
                    value={formData.contact.title} 
                    onChange={handleChange}
                    placeholder="e.g., CTO, Integration Manager"
                  />
                </FormControl>
              </GridItem>
              
              <GridItem colSpan={[2, 1]}>
                <FormControl isRequired>
                  <FormLabel>Email</FormLabel>
                  <Input 
                    name="contact.email" 
                    value={formData.contact.email} 
                    onChange={handleChange}
                    placeholder="contact@example.com"
                    type="email"
                  />
                </FormControl>
              </GridItem>
              
              <GridItem colSpan={[2, 1]}>
                <FormControl>
                  <FormLabel>Phone</FormLabel>
                  <Input 
                    name="contact.phone" 
                    value={formData.contact.phone} 
                    onChange={handleChange}
                    placeholder="(555) 123-4567"
                  />
                </FormControl>
              </GridItem>
            </Grid>
            
            <Divider />
            
            <Heading as="h3" size="md">Technical Integration</Heading>
            
            <Grid templateColumns="repeat(2, 1fr)" gap={6}>
              <GridItem colSpan={2}>
                <FormControl>
                  <FormLabel>API Documentation URL</FormLabel>
                  <Input 
                    name="integration_info.api_documentation" 
                    value={formData.integration_info.api_documentation} 
                    onChange={handleChange}
                    placeholder="https://developer.example.com/docs"
                  />
                </FormControl>
              </GridItem>
              
              <GridItem colSpan={1}>
                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Requires OAuth?</FormLabel>
                  <Checkbox 
                    name="integration_info.requires_oauth"
                    isChecked={formData.integration_info.requires_oauth}
                    onChange={handleChange}
                    size="lg"
                  />
                </FormControl>
              </GridItem>
              
              <GridItem colSpan={1}>
                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Supports FHIR?</FormLabel>
                  <Checkbox 
                    name="integration_info.supports_fhir"
                    isChecked={formData.integration_info.supports_fhir}
                    onChange={handleChange}
                    size="lg"
                  />
                </FormControl>
              </GridItem>
            </Grid>
            
            <FormControl>
              <FormLabel>Additional Notes</FormLabel>
              <Textarea 
                name="notes" 
                value={formData.notes} 
                onChange={handleChange}
                placeholder="Any additional information regarding your integration or requirements"
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
              Submit Registration
            </Button>
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
};

export default ProviderRegistrationForm;
