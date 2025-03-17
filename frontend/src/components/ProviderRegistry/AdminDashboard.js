import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Tabs, 
  TabList, 
  TabPanels, 
  Tab, 
  TabPanel, 
  Heading, 
  Text,
  useToast,
  Flex,
  Button,
  Spinner,
  Container
} from '@chakra-ui/react';
import { API_BASE_URL } from '../../config';
import ProviderRequestsTable from './ProviderRequestsTable';
import PatientRequestsTable from './PatientRequestsTable';
import RegisteredProvidersTable from './RegisteredProvidersTable';

/**
 * Admin Dashboard for managing provider registration requests
 * and approving/rejecting provider registrations
 */
const AdminDashboard = ({ token }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [providerRequests, setProviderRequests] = useState([]);
  const [patientRequests, setPatientRequests] = useState([]);
  const [registeredProviders, setRegisteredProviders] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  
  const toast = useToast();

  // Fetch all data
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        // Fetch provider registration requests
        const providerRequestsResponse = await fetch(
          `${API_BASE_URL}/api/provider-registry/admin/provider-requests`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
        
        // Fetch patient provider requests
        const patientRequestsResponse = await fetch(
          `${API_BASE_URL}/api/provider-registry/admin/patient-requests`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
        
        // Fetch registered providers
        const registeredProvidersResponse = await fetch(
          `${API_BASE_URL}/api/provider-registry/providers`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
        
        if (!providerRequestsResponse.ok || !patientRequestsResponse.ok || !registeredProvidersResponse.ok) {
          throw new Error('Failed to fetch data');
        }
        
        const providerRequestsData = await providerRequestsResponse.json();
        const patientRequestsData = await patientRequestsResponse.json();
        const registeredProvidersData = await registeredProvidersResponse.json();
        
        setProviderRequests(providerRequestsData || []);
        setPatientRequests(patientRequestsData || []);
        setRegisteredProviders(registeredProvidersData || []);
      } catch (error) {
        toast({
          title: 'Error fetching data',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [token, refreshTrigger]);

  // Handle approving a provider request
  const handleApproveProvider = async (requestId) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/provider-registry/admin/provider-request/${requestId}/approve`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to approve provider');
      }
      
      toast({
        title: 'Provider approved',
        description: 'The provider request was approved successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      // Refresh data
      setRefreshTrigger(prev => prev + 1);
    } catch (error) {
      toast({
        title: 'Error approving provider',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  // Handle updating provider status
  const handleUpdateProviderStatus = async (providerId, status) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/provider-registry/admin/provider/${providerId}/update-status`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ status })
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to update provider status');
      }
      
      toast({
        title: 'Provider status updated',
        description: `Provider status was updated to ${status}`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      // Refresh data
      setRefreshTrigger(prev => prev + 1);
    } catch (error) {
      toast({
        title: 'Error updating provider status',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  return (
    <Container maxW="container.xl" p={5}>
      <Box mb={5}>
        <Heading as="h1" size="xl">Provider Registry Admin Dashboard</Heading>
        <Text mt={2} color="gray.600">
          Manage provider registrations, patient requests, and active providers
        </Text>
      </Box>
      
      <Flex justify="flex-end" mb={4}>
        <Button 
          colorScheme="blue" 
          onClick={() => setRefreshTrigger(prev => prev + 1)}
          leftIcon={<span>🔄</span>}
        >
          Refresh Data
        </Button>
      </Flex>
      
      {isLoading ? (
        <Flex justify="center" align="center" h="300px">
          <Spinner size="xl" thickness="4px" speed="0.65s" color="blue.500" />
        </Flex>
      ) : (
        <Tabs 
          isLazy 
          colorScheme="blue" 
          variant="enclosed"
          index={activeTab}
          onChange={(index) => setActiveTab(index)}
        >
          <TabList mb="1em">
            <Tab>Provider Registration Requests ({providerRequests.length})</Tab>
            <Tab>Patient Provider Requests ({patientRequests.length})</Tab>
            <Tab>Registered Providers ({registeredProviders.length})</Tab>
          </TabList>
          
          <TabPanels>
            <TabPanel>
              <ProviderRequestsTable 
                providerRequests={providerRequests} 
                onApprove={handleApproveProvider}
              />
            </TabPanel>
            
            <TabPanel>
              <PatientRequestsTable 
                patientRequests={patientRequests}
              />
            </TabPanel>
            
            <TabPanel>
              <RegisteredProvidersTable 
                providers={registeredProviders}
                onUpdateStatus={handleUpdateProviderStatus}
              />
            </TabPanel>
          </TabPanels>
        </Tabs>
      )}
    </Container>
  );
};

export default AdminDashboard;
